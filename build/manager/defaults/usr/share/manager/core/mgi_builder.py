import json
import logging
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
from typing import Callable

import httpx
import yaml
from jinja2 import Template

from core.redis import get_redis_connection
from core.config import (
    FQDN,
    FQDN_IP,
    STACK,
    MGI_POOL_DIR,
    MGI_TEMP_DIR,
    MGI_PREFIX,
    CORE_TOKEN_URL,
    PATH_DATASHARES,
    get_dns_servers,
    HTTP_PROXY,
    HTTPS_PROXY,
    NO_PROXY,
)

SYSTEM_UUID = "71656d75-a1b2-c3d4-e5f6-7890abcdef02"

logger = logging.getLogger(__name__)


def _ensure_builder_computer_in_db(project_id: int, flavour_id: int = None):
    """
    Ensure the builder computer identity (UUID = '71656d75-a1b2-c3d4-e5f6-7890abcdef02')
    is registered in client_computer for the specified project and has the flavour's tags.
    """
    from core.database import get_db_connection

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, project_id FROM client_computer WHERE uuid = %s;",
                (SYSTEM_UUID.upper(),)
            )
            row = cur.fetchone()
            if row:
                existing_id, existing_project_id = row
                if existing_project_id != project_id:
                    logger.info(f"Updating builder computer {SYSTEM_UUID} project assignment to {project_id}...")
                    cur.execute(
                        "UPDATE client_computer SET project_id = %s, updated_at = NOW() WHERE id = %s;",
                        (project_id, existing_id)
                    )
                computer_id = existing_id
            else:
                logger.info(f"Pre-registering builder computer {SYSTEM_UUID} in database for project {project_id}...")
                cur.execute(
                    """
                    INSERT INTO client_computer (
                        uuid, status, name, fqdn, created_at, updated_at, machine, project_id
                    ) VALUES (
                        %s, 'intended', 'mgi-builder', 'mgi-builder', NOW(), NOW(), 'P', %s
                    ) RETURNING id;
                    """,
                    (SYSTEM_UUID.upper(), project_id)
                )
                computer_id = cur.fetchone()[0]

            # Sync flavour tags to client_computer_tags for this computer
            if flavour_id is not None:
                logger.info(f"Syncing tags for flavour {flavour_id} to builder computer {computer_id}...")
                
                # Fetch flavour tag attributes
                cur.execute(
                    "SELECT serverattribute_id FROM mgi_flavour_tags WHERE flavour_id = %s;",
                    (flavour_id,)
                )
                tag_ids = [r[0] for r in cur.fetchall()]
                
                # Delete existing tags for the builder computer
                cur.execute(
                    "DELETE FROM client_computer_tags WHERE computer_id = %s;",
                    (computer_id,)
                )
                
                # Insert the new flavour tags
                for tag_id in tag_ids:
                    cur.execute(
                        "INSERT INTO client_computer_tags (computer_id, serverattribute_id) VALUES (%s, %s);",
                        (computer_id, tag_id)
                    )

            conn.commit()
            logger.info("Builder computer pre-registered and tags synchronized successfully")



def _ensure_builder_certificate(project_id: int) -> tuple[Path, Path]:
    """
    Ensure client certificate and decrypted private key exist for the builder UUID on the specified project.
    Returns (cert_path, decrypted_key_path).
    """
    import asyncio
    from core.security import create_computer_cert
    from core.config import PATH_CERTIFICATES, STACK, FQDN
    from core.utils import get_host

    common_name = f"{SYSTEM_UUID}_{project_id}"
    cert_dir = PATH_CERTIFICATES / STACK / "computer" / "certs"
    cert_dir.mkdir(parents=True, exist_ok=True)

    cert_path = cert_dir / f"{common_name}.crt"
    key_path = cert_dir / f"{common_name}.key"
    decrypted_key_path = cert_dir / f"{common_name}.decrypted.key"

    password = "migasfree_builder_secure_pass"

    if not cert_path.exists() or not key_path.exists():
        logger.info(f"Generating builder certificate for CN {common_name}...")
        host = get_host(STACK)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(
            create_computer_cert(
                fqdn=FQDN,
                host=host,
                stack=STACK,
                common_name=common_name,
                password=password,
                days="7305",
                email="builder@migasfree.org",
            )
        )
        if not success:
            raise RuntimeError(f"Failed to generate builder certificate for CN {common_name}")

    if not decrypted_key_path.exists():
        logger.info(f"Decrypting builder private key for CN {common_name}...")
        cmd = [
            "openssl", "rsa",
            "-in", str(key_path),
            "-passin", f"pass:{password}",
            "-out", str(decrypted_key_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to decrypt builder private key: {res.stderr}")

    return cert_path, decrypted_key_path


MGI_QUEUE_KEY = "mgi:build_queue"
MGI_TASK_PREFIX = "mgi:task:"


TEMPLATE_DIR = Path("/usr/share/manager/templates")
MPI_TEMPLATE = "mpi.Dockerfile.j2"


def _get_core_token():
    try:
        superadmin_name = open(f"/run/secrets/{STACK}_superadmin_name", "r").read().strip()
        superadmin_pass = open(f"/run/secrets/{STACK}_superadmin_pass", "r").read().strip()
    except FileNotFoundError:
        logger.error("Superadmin secrets not found")
        return None

    data = {"username": superadmin_name, "password": superadmin_pass}
    headers = {"Content-Type": "application/json"}
    try:
        response = httpx.post(
            f"{CORE_TOKEN_URL.replace('/api/v1/token', '')}/token-auth/",
            json=data,
            headers=headers,
        )
        if response.status_code == 200:
            tokens = response.json()
            return tokens.get("token")
    except Exception as e:
        logger.error(f"Error getting core token: {e}")
    return None


def _get_core_resource(endpoint: str):
    token = _get_core_token()
    if not token:
        raise RuntimeError("Could not obtain Core API token")

    headers = {"accept": "application/json", "Authorization": f"Token {token}"}
    try:
        core_api_url = CORE_TOKEN_URL.replace("/token", "")
        response = httpx.get(
            f"{core_api_url}{endpoint}",
            headers=headers,
            follow_redirects=False,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Core API returned {response.status_code} for endpoint {endpoint}: {response.text}")
        return response.json()
    except httpx.RequestError as e:
        raise RuntimeError(f"Error calling Core API: {e}")


def _post_core_resource(endpoint: str, data: dict):
    token = _get_core_token()
    if not token:
        raise RuntimeError("Could not obtain Core API token")

    headers = {"accept": "application/json", "Content-Type": "application/json", "Authorization": f"Token {token}"}
    try:
        core_api_url = CORE_TOKEN_URL.replace("/token", "")
        response = httpx.post(
            f"{core_api_url}{endpoint}",
            json=data,
            headers=headers,
            follow_redirects=False,
        )
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Core API returned {response.status_code} for endpoint {endpoint}: {response.text}")
        return response.json()
    except httpx.RequestError as e:
        raise RuntimeError(f"Error calling Core API: {e}")


def _patch_core_resource(endpoint: str, data: dict):
    token = _get_core_token()
    if not token:
        raise RuntimeError("Could not obtain Core API token")

    headers = {"accept": "application/json", "Content-Type": "application/json", "Authorization": f"Token {token}"}
    try:
        core_api_url = CORE_TOKEN_URL.replace("/token", "")
        response = httpx.patch(
            f"{core_api_url}{endpoint}",
            json=data,
            headers=headers,
            follow_redirects=False,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Core API returned {response.status_code} for endpoint {endpoint}: {response.text}")
        return response.json()
    except httpx.RequestError as e:
        raise RuntimeError(f"Error calling Core API: {e}")


def _get_project_from_core(project_id: int):
    # Endpoint expects something like /token/projects/1/
    return _get_core_resource(f"/token/projects/{project_id}/")


def _get_release_from_core(release_id: int) -> dict:
    return _get_core_resource(f"/token/mgi/release/{release_id}/")


def _get_config_from_core(config_id: int) -> dict:
    return _get_core_resource(f"/token/mgi/config/{config_id}/")


def _get_flavours_from_core(config_id: int) -> list[dict]:
    # Use filtering query parameter to get flavours for a specific config
    return _get_core_resource(f"/token/mgi/flavour/?config={config_id}")


def _create_build_record(release_id: int, flavour_id: int, task_id: str):
    data = {
        "release": release_id,
        "flavour": flavour_id,
        "task_id": task_id,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    logger.debug(f"Creating MGI Build record: {data}")
    return _post_core_resource("/token/mgi/build/", data)


def _update_build_record(build_id: int, status: str, uri: str = None, size: int = None, log: str = None):
    data = {"status": status}
    if uri is not None:
        data["uri"] = uri
    if size is not None:
        data["size"] = size
    if log is not None:
        data["log"] = log

    if status in ("completed", "failed"):
        data["finished_at"] = datetime.now(timezone.utc).isoformat()
        logger.debug(f"Updating MGI Build {build_id} to {status} at {data['finished_at']}")

    return _patch_core_resource(f"/token/mgi/build/{build_id}/", data)


def _update_task_status(task_id: str, status: str, progress: int = 0, message: str = ""):
    con = get_redis_connection()
    key = f"{MGI_TASK_PREFIX}{task_id}"
    con.hset(
        key,
        mapping={
            "status": status,
            "progress": str(progress),
            "message": message,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    con.expire(key, 86400)


def generate_dockerfile(project_data: dict, config_data: dict, flavour_data: dict, build_dir: Path) -> Path:
    template = Template(config_data["dockerfile"])
    base_os = config_data.get("base_os", "")
    if not base_os:
        raise ValueError("Project has no base_os defined")

    dockerfile_content = template.render(
        base_os=base_os,
        server=FQDN,
        project_id=project_data.get("id"),
        project_slug=project_data.get("slug", ""),
        project_name=project_data.get("name", ""),
        prefix=MGI_PREFIX,
        user=flavour_data.get("user", "mgi"),
        password=flavour_data.get("password", "mgi"),
        keymap=flavour_data.get("keymap", "us"),
        keyboard_model=flavour_data.get("keyboard_model", "pc105"),
        charmap=flavour_data.get("charmap", "UTF-8"),
        codeset=flavour_data.get("codeset", "Lat15"),
        timezone=flavour_data.get("timezone", "UTC"),
        hostname=flavour_data.get("hostname", "mgi"),
        fqdn_ip=FQDN_IP,
        system_uuid=SYSTEM_UUID,
        tags=" ".join([t.strip() for t in flavour_data.get("tags", "").replace(",", " ").split() if t.strip()]),
    )

    # Programmatic edits for Task A (Static Builder Identity mTLS)
    # 1. Inject client certificates COPY command right before the RUN command containing migasfree conf
    lines = dockerfile_content.splitlines()
    run_idx = -1
    for i, line in enumerate(lines):
        if "migasfree conf" in line:
            # Search backwards for the nearest line starting with RUN
            for j in range(i, -1, -1):
                if lines[j].strip().startswith("RUN"):
                    run_idx = j
                    break
            break

    if run_idx != -1:
        lines.insert(run_idx, "COPY keys/ /etc/migasfree/keys/")
        # Also copy keys to the mtls path where migasfree client expects them
        mtls_setup_cmds = [
            f"RUN mkdir -p /var/migasfree-client/mtls/{FQDN}",
            f"RUN cp /etc/migasfree/keys/computer.crt /var/migasfree-client/mtls/{FQDN}/cert.pem",
            f"RUN cp /etc/migasfree/keys/computer.key /var/migasfree-client/mtls/{FQDN}/key.pem",
            f"RUN cp /etc/migasfree/keys/ca.crt /var/migasfree-client/mtls/{FQDN}/ca.pem"
        ]
        for cmd in reversed(mtls_setup_cmds):
            lines.insert(run_idx + 1, cmd)
        logger.info("Programmatically injected COPY keys/ and mtls copy commands to Dockerfile")

    # Reassemble and replace registration with true bypass
    dockerfile_content = "\n".join(lines)
    dockerfile_content = dockerfile_content.replace(
        'echo "y" | USER=root migasfree register',
        'true'
    )

    dockerfile_path = build_dir / "Dockerfile"
    dockerfile_path.write_text(dockerfile_content)
    return dockerfile_path


def build_docker_image(
    build_dir: Path,
    image_tag: str,
    progress_cb: Callable[[int, str], None] | None = None,
    task_id: str | None = None,
) -> None:

    cmd = [
        "docker",
        "build",
        "--no-cache",
    ]

    if HTTP_PROXY:
        cmd += ["--build-arg", f"http_proxy={HTTP_PROXY}", "--build-arg", f"HTTP_PROXY={HTTP_PROXY}"]
    if HTTPS_PROXY:
        cmd += ["--build-arg", f"https_proxy={HTTPS_PROXY}", "--build-arg", f"HTTPS_PROXY={HTTPS_PROXY}"]
    if NO_PROXY:
        cmd += ["--build-arg", f"no_proxy={NO_PROXY}", "--build-arg", f"NO_PROXY={NO_PROXY}"]

    fqdn_ip = FQDN_IP
    if not fqdn_ip:
        import socket
        try:
            fqdn_ip = socket.gethostbyname(FQDN)
        except Exception:
            pass

    if not fqdn_ip or fqdn_ip.startswith("127."):
        # Try to query the local Docker Swarm node IP directly via the Docker SDK
        try:
            import docker
            client = docker.from_env()
            node_info = client.info()
            node_id = node_info.get("Swarm", {}).get("NodeID")
            if node_id:
                node = client.nodes.get(node_id)
                addr = node.attrs.get("Status", {}).get("Addr")
                if addr:
                    fqdn_ip = addr
        except Exception:
            pass

    if not fqdn_ip or fqdn_ip.startswith("127."):
        # Dynamic interface fallback (offline-friendly)
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Try to connect to a local/corporate DNS server first if detected
            dns_servers = get_dns_servers()
            target_ip = dns_servers[0] if dns_servers else "8.8.8.8"
            s.connect((target_ip, 53 if dns_servers else 80))
            fqdn_ip = s.getsockname()[0]
            s.close()
        except Exception:
            pass

    if fqdn_ip:
        cmd += ["--add-host", f"{FQDN}:{fqdn_ip}"]

    cmd += [
        "--build-arg",
        f"CACHEBUST={int(time.time())}",
        "-t",
        image_tag,
        "-f",
        str(build_dir / "Dockerfile"),
        str(build_dir),
    ]
    logger.info(f"Building Docker image: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    last_step = ""
    errors = []
    for line in iter(proc.stdout.readline, ""):
        line = line.rstrip()
        if not line:
            continue
        if task_id:
            logger.info(f"Task {task_id} log: {line}")
        else:
            logger.info(f"  {line}")
        if line.startswith("Step ") and "/" in line:
            step = line.split(" :")[0] if " :" in line else line
            msg = f"Building image: {step}"
            if msg != last_step:
                last_step = msg
                if progress_cb:
                    progress_cb(0, msg)
        if "failed" in line.lower() or "error:" in line.lower() or "non-zero" in line or line.startswith("E:"):
            errors.append(line)
            if len(errors) > 5:
                errors.pop(0)
    proc.wait()
    if proc.returncode != 0:
        last_err = errors[-1] if errors else "Unknown build error"
        raise RuntimeError(f"Docker build failed: {last_err}")
    logger.info("Docker image built")


def export_and_extract(
    image_name: str,
    container_name: str,
    root_dir: Path,
    progress_cb: Callable[[int, str], None] | None = None,
) -> None:
    total_bytes = subprocess.run(
        ["docker", "image", "inspect", image_name, "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
    )
    total = int(total_bytes.stdout.strip()) if total_bytes.returncode == 0 else 0
    if total:
        logger.info(f"Image size: {total / (1024 * 1024):.0f} MiB")

    oci_dir = root_dir.parent / "oci_bundle"
    bundle_dir = root_dir.parent / "bundle"

    try:
        if progress_cb:
            progress_cb(10, "Exporting image from Docker to OCI format...")
        logger.info(f"Running skopeo copy for {image_name}")

        skopeo = subprocess.run(
            ["skopeo", "copy", f"docker-daemon:{image_name}", f"oci:{oci_dir}:latest"],
            capture_output=True,
            text=True,
        )
        if skopeo.returncode != 0:
            raise RuntimeError(f"skopeo copy failed: {skopeo.stderr}")

        if progress_cb:
            progress_cb(50, "Unpacking OCI bundle with umoci...")
        logger.info(f"Running umoci unpack for {image_name}")

        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)

        umoci = subprocess.run(
            ["umoci", "unpack", "--image", f"{oci_dir}:latest", str(bundle_dir)],
            capture_output=True,
            text=True,
        )
        if umoci.returncode != 0:
            raise RuntimeError(f"umoci unpack failed: {umoci.stderr}")

        if root_dir.exists():
            shutil.rmtree(root_dir)
        shutil.move(str(bundle_dir / "rootfs"), str(root_dir))

    finally:
        if oci_dir.exists():
            shutil.rmtree(oci_dir, ignore_errors=True)
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir, ignore_errors=True)

    logger.info(f"Image extracted to {root_dir} preserving xattrs")


def _create_ext4_image_from_dir(source_dir: Path, output_path: Path, headroom_mb: int = 16) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    du = subprocess.run(
        ["du", "-sm", str(source_dir)],
        capture_output=True,
        text=True,
    )
    src_mb = int(du.stdout.split()[0]) if du.returncode == 0 else 64
    size_mb = max(int(src_mb * 1.2) + headroom_mb, 64)

    subprocess.run(
        ["dd", "if=/dev/zero", f"of={output_path}", "bs=1M", f"count={size_mb}"],
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["mkfs.ext4", "-F", "-d", str(source_dir), str(output_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"mkfs.ext4 -d failed: {result.stderr}")

    subprocess.run(["e2fsck", "-y", "-f", str(output_path)], capture_output=True)
    # Shrink to content + headroom
    content_result = subprocess.run(
        ["dumpe2fs", "-h", str(output_path)],
        capture_output=True,
        text=True,
    )
    target_blocks = None
    if content_result.returncode == 0:
        block_size = 4096
        block_count = 0
        free_blocks = 0
        for line in content_result.stdout.splitlines():
            if line.startswith("Block size:"):
                block_size = int(line.split(":")[1].strip())
            elif line.startswith("Block count:"):
                block_count = int(line.split(":")[1].strip())
            elif line.startswith("Free blocks:"):
                free_blocks = int(line.split(":")[1].strip())
        used_blocks = block_count - free_blocks
        headroom_blocks = (headroom_mb * 1024 * 1024) // block_size
        target_blocks = used_blocks + headroom_blocks
    if target_blocks:
        subprocess.run(
            ["resize2fs", str(output_path), f"{target_blocks}"],
            capture_output=True,
            text=True,
        )
    else:
        # Fallback: don't shrink at all
        logger.warning("Could not calculate target size, keeping full image")

    uuid_result = subprocess.run(
        ["blkid", "-s", "UUID", "-o", "value", str(output_path)],
        capture_output=True,
        text=True,
    )
    fs_uuid = uuid_result.stdout.strip() if uuid_result.returncode == 0 else ""
    real_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Created {output_path.name}: {src_mb}MiB src → {real_mb:.0f}MiB UUID={fs_uuid}")
    return fs_uuid


def generate_partition_yml(output_dir: Path, config_data: dict) -> Path:
    yml_path = output_dir / "partition.yml"
    yml_path.write_text(config_data["partition"])
    return yml_path


def generate_checksums(output_dir: Path, config_data: dict) -> Path:
    checksum_path = output_dir / "checksums.sha256"
    partition_def = yaml.safe_load(config_data["partition"])
    excluded = {"BIOS", "EFI", "SWAP"}
    files = [f"{p['name']}.raw" for p in partition_def.get("partitions", []) if p["name"] not in excluded]
    files.append("partition.yml")

    lines = []
    for fname in files:
        fpath = output_dir / fname
        if fpath.exists():
            h = sha256(fpath.read_bytes()).hexdigest()
            size = fpath.stat().st_size
            lines.append(f"{h} {size} {fname}")
    checksum_path.write_text("\n".join(lines) + "\n")
    return checksum_path


def update_catalog_json(mpi_name: str, flavour_data: dict, build_id: int = None) -> None:
    catalog_path = MGI_POOL_DIR / "catalog.json"
    catalog = []
    if catalog_path.exists():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            if not isinstance(catalog, list):
                catalog = []
        except Exception as e:
            logger.error(f"Error reading catalog.json: {e}")
            catalog = []

    # Check if entry already exists
    entry_found = False
    enabled = False
    description = flavour_data.get("description", "")

    for entry in catalog:
        if isinstance(entry, dict) and entry.get("name") == mpi_name:
            entry["enabled"] = enabled
            entry["description"] = description
            if build_id is not None:
                entry["build_id"] = build_id
            entry_found = True
            break

    if not entry_found:
        new_entry = {"name": mpi_name, "enabled": enabled, "description": description}
        if build_id is not None:
            new_entry["build_id"] = build_id
        catalog.append(new_entry)

    try:
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["chown", "890:890", str(catalog_path)], check=True)
        logger.info(f"Updated catalog.json successfully for {mpi_name}")
    except Exception as e:
        logger.error(f"Failed to update catalog.json: {e}")


def build_mgi_image(task_id: str, release_id: int):
    _update_task_status(task_id, "fetching", 0, "Fetching release and project data")

    # Check if there is no MCS ISO in the pool directory. If so, automatically queue an MCS build task!
    try:
        mcs_pool_dir = PATH_DATASHARES / STACK / "pool" / "mcs"
        iso_files = list(mcs_pool_dir.glob("*.iso")) if mcs_pool_dir.exists() else []
        if not iso_files:
            logger.info(f"Task {task_id}: No MCS ISO found in pool. Queueing automatic MCS build task sequentially...")
            con = get_redis_connection()
            mcs_task_id = str(uuid.uuid4())
            con.rpush(
                "mcs:build_queue",
                json.dumps(
                    {
                        "task_id": mcs_task_id,
                        "server_url": None,
                        "server_ip": None,
                        "keymap": None,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                ),
            )
            con.hset(
                f"mcs:task:{mcs_task_id}",
                mapping={
                    "status": "queued",
                    "progress": "0",
                    "message": "Enqueued automatically by MGI build trigger",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            con.expire(f"mcs:task:{mcs_task_id}", 86400)
            logger.info(f"Task {task_id}: Automatic MCS build task {mcs_task_id} successfully queued.")
    except Exception as ex:
        logger.error(f"Task {task_id}: Failed to queue automatic MCS build task: {ex}")

    try:
        # mgi_release → mgi_config → core_project
        release_data = _get_release_from_core(release_id)
        config_id = release_data.get("config")
        config_data = _get_config_from_core(config_id)
        project_id = config_data.get("project")
        project_data = _get_project_from_core(project_id)

        # In DRF, list endpoints usually return a dict with a "results" array if paginated
        flavours_response = _get_flavours_from_core(config_id)
        flavours_list = (
            flavours_response.get("results", flavours_response)
            if isinstance(flavours_response, dict)
            else flavours_response
        )

        flavours_data = [f for f in flavours_list if f.get("enabled", True)]
    except Exception as e:
        logger.error(f"Task {task_id}: Build failed: {e}")
        _update_task_status(task_id, "error", 0, str(e))
        return

    slug = project_data.get("slug", str(project_id))
    num_flavours = len(flavours_data)

    if num_flavours == 0:
        _update_task_status(task_id, "error", 0, "No flavours found for project")
        return

    try:
        for i, flavour in enumerate(flavours_data):
            base_pct = int((i / num_flavours) * 100)
            flavour_span = 100 / num_flavours

            mpi_name = f"{project_data.get('name', slug)}-{release_data['name']}-{flavour['name']}".lower()

            def _flavour_progress(pct, msg):
                actual_pct = base_pct + int((pct / 100) * flavour_span)
                _update_task_status(task_id, "building MPI", actual_pct, f"[{mpi_name}] {msg}")

            build_dir = MGI_TEMP_DIR / f"{mpi_name}-{task_id[:8]}"
            image_tag = f"mgi/{mpi_name}:{task_id[:8]}"
            container_name = f"mgi-{mpi_name}-{task_id[:8]}"
            root_dir = build_dir / "root"
            pool_dir = MGI_POOL_DIR / mpi_name

            build_dir.mkdir(parents=True, exist_ok=True)

            _flavour_progress(5, "Generating Dockerfile")

            # Create build record in Core
            build_record = None
            try:
                build_record = _create_build_record(release_id, flavour["id"], task_id)
            except Exception as e:
                logger.error(f"Task {task_id}: Could not create build record in Core: {e}")

            # Ensure builder computer in DB and generate certificates
            try:
                _ensure_builder_computer_in_db(project_id, flavour["id"])
                cert_path, decrypted_key_path = _ensure_builder_certificate(project_id)
                
                keys_dest = build_dir / "keys"
                keys_dest.mkdir(parents=True, exist_ok=True)
                shutil.copy(cert_path, keys_dest / "computer.crt")
                shutil.copy(decrypted_key_path, keys_dest / "computer.key")
                logger.info("Builder certificates injected into build context keys/")
            except Exception as e:
                logger.error(f"Task {task_id}: Failed to ensure or inject builder certificates: {e}")
                raise

            generate_dockerfile(project_data, config_data, flavour, build_dir)

            # Copy certificate to build context
            cert_name = f"ca-{FQDN}.crt"
            src_cert = MGI_POOL_DIR.parent / "install" / cert_name
            if src_cert.exists():
                dest_dir = build_dir / "pool" / "install"
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_cert, dest_dir / cert_name)
                logger.info(f"Copied {src_cert} to {dest_dir}")
                
                # Also copy CA to keys/ for local validation if needed
                shutil.copy(src_cert, build_dir / "keys" / "ca.crt")
            else:
                logger.warning(f"Certificate {src_cert} not found")

            _flavour_progress(15, "Building Docker image")
            build_docker_image(build_dir, image_tag, progress_cb=_flavour_progress, task_id=task_id)

            _flavour_progress(35, "Exporting and extracting root filesystem")
            export_and_extract(image_tag, container_name, root_dir, progress_cb=_flavour_progress)

            _flavour_progress(38, "Configuring network, hosts and keyboard")
            etc_dir = root_dir / "etc"
            flavour_hostname = flavour.get("hostname", "mgi")
            (etc_dir / "hostname").write_text(f"{flavour_hostname}\n")
            hosts_content = (
                f"127.0.0.1 localhost {flavour_hostname}\n::1 localhost ip6-localhost ip6-loopback {flavour_hostname}\n"
            )
            if FQDN_IP:
                hosts_content += f"{FQDN_IP} {FQDN}\n"
            (etc_dir / "hosts").write_text(hosts_content)
            resolv_conf = etc_dir / "resolv.conf"
            if resolv_conf.exists() or resolv_conf.is_symlink():
                resolv_conf.unlink()
            resolv_conf.symlink_to("/run/systemd/resolve/stub-resolv.conf")

            partition_def = yaml.safe_load(config_data["partition"])
            excluded = {"BIOS", "EFI", "SWAP"}
            raw_partitions = [p for p in partition_def.get("partitions", []) if p["name"] not in excluded]

            for part in raw_partitions:
                name = part["name"]
                raw_path = build_dir / f"{name}.raw"
                source_dir = root_dir / part["mount"].lstrip("/")
                if not source_dir.exists():
                    source_dir.mkdir(parents=True, exist_ok=True)

                if name == "SYSTEM":
                    (source_dir / "boot" / "grub").mkdir(parents=True, exist_ok=True)
                    (source_dir / "boot" / "efi").mkdir(parents=True, exist_ok=True)

                headroom = 128 if name == "SYSTEM" else 8
                _flavour_progress(55, f"Creating {name}.raw")
                _create_ext4_image_from_dir(source_dir, raw_path, headroom_mb=headroom)

            _flavour_progress(80, "Generating metadata")
            generate_partition_yml(build_dir, config_data)
            generate_checksums(build_dir, config_data)

            _flavour_progress(90, "Moving files to pool directory")
            pool_dir.mkdir(parents=True, exist_ok=True)
            for part in raw_partitions:
                f = f"{part['name']}.raw"
                fpath = build_dir / f
                if fpath.exists():
                    shutil.move(str(fpath), str(pool_dir / f))
            for f in ["partition.yml", "checksums.sha256"]:
                fpath = build_dir / f
                if fpath.exists():
                    shutil.move(str(fpath), str(pool_dir / f))

            _flavour_progress(95, "Setting permissions")
            subprocess.run(["chown", "-R", "890:890", str(MGI_POOL_DIR)], check=True)

            try:
                build_id_val = build_record["id"] if build_record else None
                update_catalog_json(mpi_name, flavour, build_id=build_id_val)
            except Exception as ce:
                logger.error(f"Failed to update catalog.json: {ce}")

            _cleanup_build(build_dir, image_tag)

            if build_record:
                try:
                    uri = f"https://{FQDN}/pool/mgi/{mpi_name}/"
                    size = (pool_dir / "SYSTEM.raw").stat().st_size if (pool_dir / "SYSTEM.raw").exists() else 0
                    success_log = (
                        f"Build completed successfully for {mpi_name}. All partitions created and metadata generated."
                    )
                    _update_build_record(build_record["id"], "completed", uri=uri, size=size, log=success_log)
                except Exception as e:
                    logger.error(f"Task {task_id}: Could not update build record to completed in Core: {e}")

        _update_task_status(task_id, "completed", 100, "Build completed successfully")
        logger.info(f"Task {task_id}: Build completed for release {release_id}")

    except Exception as e:
        logger.error(f"Task {task_id}: Build failed: {e}")
        _update_task_status(task_id, "error", 0, str(e))
        if "build_record" in locals() and build_record:
            try:
                _update_build_record(build_record["id"], "failed", log=str(e))
            except Exception as e2:
                logger.error(f"Task {task_id}: Could not update build record to failed in Core: {e2}")
        try:
            _cleanup_build(build_dir, image_tag)
        except Exception:
            pass


def _cleanup_build(build_dir: Path, image_tag: str) -> None:
    subprocess.run(["docker", "rmi", "-f", image_tag], capture_output=True)
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)


def _mgi_worker():
    con = get_redis_connection()
    logger.info("MGI build worker started")
    while True:
        try:
            result = con.blpop(MGI_QUEUE_KEY, timeout=5)
            if result is None:
                continue
            _, task_data = result
            task = json.loads(task_data) if isinstance(task_data, str) else json.loads(task_data.decode("utf-8"))
            task_id = task.get("task_id", str(uuid.uuid4()))
            release_id = task.get("release_id")
            logger.info(f"MGI worker processing task {task_id} for release {release_id}")
            _update_task_status(task_id, "queued", 0, "Task accepted, starting build")
            build_mgi_image(task_id, release_id)
        except Exception as e:
            logger.error(f"MGI worker error: {e}")
            time.sleep(5)
            try:
                con = get_redis_connection()
            except Exception:
                pass


def start_mgi_worker():
    import asyncio

    def _run_worker():
        try:
            _mgi_worker()
        except Exception as e:
            logger.error(f"MGI worker crashed: {e}")

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_worker)
    logger.info("MGI build worker registered")

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
    STACK,
    MCS_POOL_DIR,
    MCS_TEMP_DIR,
    MCS_PREFIX,
    CORE_TOKEN_URL,
)

logger = logging.getLogger(__name__)

MCS_QUEUE_KEY = "mcs:build_queue"
MCS_TASK_PREFIX = "mcs:task:"

TEMPLATE_DIR = Path("/usr/share/manager/templates")
MPI_TEMPLATE = "mpi.Dockerfile.j2"


def _get_core_token():
    try:
        superadmin_name = (
            open(f"/run/secrets/{STACK}_superadmin_name", "r").read().strip()
        )
        superadmin_pass = (
            open(f"/run/secrets/{STACK}_superadmin_pass", "r").read().strip()
        )
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


def _get_project_from_core(project_id: int):
    token = _get_core_token()
    if not token:
        raise RuntimeError("Could not obtain Core API token")

    headers = {"accept": "application/json", "Authorization": f"Token {token}"}
    try:
        response = httpx.get(
            f"{CORE_TOKEN_URL}/projects/{project_id}/",
            headers=headers,
            follow_redirects=False,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Core API returned {response.status_code} for project {project_id}"
            )
        return response.json()
    except httpx.RequestError as e:
        raise RuntimeError(f"Error calling Core API: {e}")


def _get_partition_mockup() -> str:
    return """# MCS Partition Definition
# Sizes are in MB.
# Type GUIDs for GPT:
# - EFI: C12A7328-F81F-11D2-BA4B-00A0C93EC93B
# - BIOS: 21686148-6449-6E6F-744E-656564454649
# - SWAP: 0657FD6D-A4AB-43C4-84E5-0933C84B4F4F
# - Linux: 0FC63DAF-8483-4772-8E79-3D69D8477DE4

partitions:
  - number: 1
    name: "EFI"
    size: 512
    type: "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
    filesystem: "vfat"
    mount: "/boot/efi"

  - number: 2
    name: "BIOS"
    size: 1
    type: "21686148-6449-6E6F-744E-656564454649"
    filesystem: null
    mount: "none"

  - number: 3
    name: "SWAP"
    size: 2048
    type: "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F"
    filesystem: "swap"
    mount: "none"

  - number: 4
    name: "SYSTEM"
    size: 20480
    type: "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
    filesystem: "ext4"
    mount: "/"

  - number: 5
    name: "HOME"
    size: 0  # 0 means use the rest of the disk
    type: "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
    filesystem: "ext4"
    mount: "/home"
"""


def _get_release_mockup(release_id: int) -> dict:
    dockerfile_content = """FROM debian:13.4

ARG CACHEBUST=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        ca-certificates \\
        curl \\
        wget \\
        gnupg \\
        systemd \\
        systemd-sysv \\
        systemd-resolved \\
        udev \\
        dbus \\
        procps \\
        iproute2 \\
        net-tools \\
        sudo \\
        locales \\
        tzdata \\
        efibootmgr \\
        openssh-server \\
        os-prober \\
        kmod \\
        pciutils \\
        console-setup \\
        console-data \\
        kbd \\
        parted \\
        nano \\
        bzip2 \\
        zstd \\
        e2fsprogs \\
        iputils-ping \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

RUN . /etc/os-release && \\
    case "$ID" in \\
        ubuntu) KERNEL_PKG="linux-generic" ;; \\
        debian) KERNEL_PKG="linux-image-amd64" ;; \\
        *)      KERNEL_PKG="linux-image-generic" ;; \\
    esac && \\
    apt-get update && \\
    apt-get install -y --no-install-recommends "$KERNEL_PKG"

RUN echo "172.0.0.10 {{ server }}" >> /etc/hosts

# The public certificate from the certification authority.
RUN wget --no-check-certificate -O /usr/local/share/ca-certificates/{{ server }}.crt http://{{ server }}/pool/install/ca-{{ server }}.crt  && \\
    update-ca-certificates --fresh

RUN wget http://{{ server }}/public/lnx-1/stores/thirds/migasfree-client_5.0-1_all.deb && \\
    apt install -y ./migasfree-client_5.0-1_all.deb && \\
    rm -f migasfree-client_5.0-1_all.deb && \\
    migasfree conf --server {{ server }} --project LNX-1 && \\
    PYTHONHTTPSVERIFY=0 migasfree sync

RUN echo "grub-pc grub-pc/install_devices_empty boolean true" | debconf-set-selections && \\
    echo "grub-pc grub-pc/install_devices string " | debconf-set-selections && \\
    apt-get install -y --no-install-recommends grub-common grub-pc-bin grub-efi-amd64-bin && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \\
    echo "es_ES.UTF-8 UTF-8" >> /etc/locale.gen && \\
    locale-gen

RUN echo "LANG=en_US.UTF-8" > /etc/default/locale

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV TZ={{ timezone }}

RUN ln -fs /usr/share/zoneinfo/{{ timezone }} /etc/localtime && \\
    dpkg-reconfigure -f noninteractive tzdata

RUN install -d -m 0755 /etc/{{ prefix }} && \\
    echo '{"server":"{{ server }}","project":"{{ project_slug }}","project_name":"{{ project_name }}","prefix":"{{ prefix }}"}' > /etc/{{ prefix }}/project.json

RUN mkdir -p /etc/systemd/network && \\
    echo "[Match]\\nName=en* eth*\\n\\n[Network]\\nDHCP=yes" > /etc/systemd/network/20-wired.network

RUN mkdir -p /etc/systemd/resolved.conf.d && \\
    echo "[Resolve]\\nFallbackDNS=8.8.8.8 1.1.1.1" > /etc/systemd/resolved.conf.d/fallback.conf

RUN systemctl enable systemd-networkd.service 2>/dev/null; \\
    systemctl enable systemd-resolved.service 2>/dev/null; \\
    exit 0

RUN printf 'XKBMODEL="{{ keyboard_model }}"\\nXKBLAYOUT="{{ keymap }}"\\nXKBVARIANT=""\\nXKBOPTIONS=""\\nBACKSPACE="guess"\\n' > /etc/default/keyboard && \\
    printf 'ACTIVE_CONSOLES="/dev/tty[1-6]"\\nCHARMAP="{{ charmap }}"\\nCODESET="{{ codeset }}"\\nFONTFACE="Fixed"\\nFONTSIZE="16"\\n' > /etc/default/console-setup && \\
    setupcon --save-only

RUN adduser --disabled-password --gecos "" {{ user }} && \\
    echo "{{ user }}:{{ password }}" | chpasswd && \\
    usermod -aG sudo,users {{ user }} && \\
    mkdir -p /home/{{ user }} && \\
    chown {{ user }}:{{ user }} /home/{{ user }} && \\
    chmod 700 /home/{{ user }}




CMD ["/sbin/init"]
"""
    return {
        "id": release_id,
        "name": "3",
        "project_id": 2,
        "dockerfile": dockerfile_content,
        "partition": _get_partition_mockup(),
    }


def _get_flavours_mockup(project_id: int) -> list[dict]:
    return [
        {
            "id": 1,
            "name": "std",
            "project_id": project_id,
            "tags": "",
            "description": "Standard",
            "enabled": True,
            "user": "alberto",
            "password": "alberto",
            "keymap": "es",
            "keyboard_model": "pc105",
            "charmap": "UTF-8",
            "codeset": "Lat15",
            "timezone": "Europe/Madrid",
            "hostname": "alberto",
        },
        {
            "id": 2,
            "name": "senior",
            "project_id": project_id,
            "tags": "senior",
            "description": "Senior",
            "enabled": False,
            "user": "senior",
            "password": "senior",
            "keymap": "es",
            "keyboard_model": "pc105",
            "charmap": "UTF-8",
            "codeset": "Lat15",
            "timezone": "Europe/Madrid",
            "hostname": "senior",
        },
    ]


def _update_task_status(
    task_id: str, status: str, progress: int = 0, message: str = ""
):
    con = get_redis_connection()
    key = f"{MCS_TASK_PREFIX}{task_id}"
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


def generate_dockerfile(
    project_data: dict, release_data: dict, flavour_data: dict, build_dir: Path
) -> Path:
    template = Template(release_data["dockerfile"])
    base_os = project_data.get("base_os", "")
    if not base_os:
        raise ValueError("Project has no base_os defined")

    dockerfile_content = template.render(
        base_os=base_os,
        server=FQDN,
        project_slug=project_data.get("slug", str(project_data.get("id"))),
        project_name=project_data.get("name", ""),
        prefix=MCS_PREFIX,
        user=flavour_data.get("user", "mcs"),
        password=flavour_data.get("password", "mcs"),
        keymap=flavour_data.get("keymap", "us"),
        keyboard_model=flavour_data.get("keyboard_model", "pc105"),
        charmap=flavour_data.get("charmap", "UTF-8"),
        codeset=flavour_data.get("codeset", "Lat15"),
        timezone=flavour_data.get("timezone", "UTC"),
        hostname=flavour_data.get("hostname", "mcs"),
    )

    dockerfile_path = build_dir / "Dockerfile"
    dockerfile_path.write_text(dockerfile_content)
    return dockerfile_path


def build_docker_image(
    build_dir: Path,
    image_tag: str,
    progress_cb: Callable[[int, str], None] | None = None,
) -> None:
    cmd = [
        "docker",
        "build",
        "--no-cache",
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
        logger.info(f"  {line}")
        if line.startswith("Step ") and "/" in line:
            step = line.split(" :")[0] if " :" in line else line
            msg = f"Building image: {step}"
            if msg != last_step:
                last_step = msg
                if progress_cb:
                    progress_cb(0, msg)
        if (
            "failed" in line.lower()
            or "error:" in line.lower()
            or "non-zero" in line
            or line.startswith("E:")
        ):
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


def _create_ext4_image_from_dir(
    source_dir: Path, output_path: Path, headroom_mb: int = 16
) -> str:
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
    logger.info(
        f"Created {output_path.name}: {src_mb}MiB src → {real_mb:.0f}MiB UUID={fs_uuid}"
    )
    return fs_uuid


def generate_partition_yml(output_dir: Path, release_data: dict) -> Path:
    yml_path = output_dir / "partition.yml"
    yml_path.write_text(release_data["partition"])
    return yml_path


def generate_checksums(output_dir: Path, release_data: dict) -> Path:
    checksum_path = output_dir / "checksums.sha256"
    partition_def = yaml.safe_load(release_data["partition"])
    excluded = {"BIOS", "EFI", "SWAP"}
    files = [
        f"{p['name']}.raw"
        for p in partition_def.get("partitions", [])
        if p["name"] not in excluded
    ]
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


def update_projects_json(
    output_dir: Path, project_slug: str, project_data: dict
) -> Path:
    projects_path = output_dir / "projects.json"
    projects = {}
    if projects_path.exists():
        try:
            projects = json.loads(projects_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            projects = {}
    projects[project_slug] = {
        "name": project_data.get("name", project_slug),
        "slug": project_slug,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    projects_path.write_text(json.dumps(projects, indent=2))
    return projects_path


def build_mcs_image(task_id: str, release_id: int):
    _update_task_status(task_id, "fetching", 0, "Fetching release and project data")
    try:
        release_data = _get_release_mockup(release_id)
        project_id = release_data.get("project_id")
        project_data = _get_project_from_core(project_id)
        flavours_data = [
            f for f in _get_flavours_mockup(project_id) if f.get("enabled", True)
        ]
    except Exception as e:
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
                _update_task_status(
                    task_id, "building MPI", actual_pct, f"[{mpi_name}] {msg}"
                )

            build_dir = MCS_TEMP_DIR / f"{mpi_name}-{task_id[:8]}"
            image_tag = f"mcs/{mpi_name}:{task_id[:8]}"
            container_name = f"mcs-{mpi_name}-{task_id[:8]}"
            root_dir = build_dir / "root"
            pool_dir = MCS_POOL_DIR / mpi_name

            build_dir.mkdir(parents=True, exist_ok=True)

            _flavour_progress(5, "Generating Dockerfile")
            generate_dockerfile(project_data, release_data, flavour, build_dir)

            _flavour_progress(15, "Building Docker image")
            build_docker_image(build_dir, image_tag, progress_cb=_flavour_progress)

            _flavour_progress(35, "Exporting and extracting root filesystem")
            export_and_extract(
                image_tag, container_name, root_dir, progress_cb=_flavour_progress
            )

            _flavour_progress(38, "Configuring network, hosts and keyboard")
            etc_dir = root_dir / "etc"
            flavour_hostname = flavour.get("hostname", "mcs")
            (etc_dir / "hostname").write_text(f"{flavour_hostname}\n")
            (etc_dir / "hosts").write_text(
                f"127.0.0.1 localhost {flavour_hostname}\n::1 localhost ip6-localhost ip6-loopback {flavour_hostname}\n"
            )
            resolv_conf = etc_dir / "resolv.conf"
            if resolv_conf.exists() or resolv_conf.is_symlink():
                resolv_conf.unlink()
            resolv_conf.symlink_to("/run/systemd/resolve/stub-resolv.conf")

            partition_def = yaml.safe_load(release_data["partition"])
            excluded = {"BIOS", "EFI", "SWAP"}
            raw_partitions = [
                p
                for p in partition_def.get("partitions", [])
                if p["name"] not in excluded
            ]

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
            generate_partition_yml(build_dir, release_data)
            generate_checksums(build_dir, release_data)
            update_projects_json(build_dir, slug, project_data)

            _flavour_progress(90, "Moving files to pool directory")
            pool_dir.mkdir(parents=True, exist_ok=True)
            for part in raw_partitions:
                f = f"{part['name']}.raw"
                fpath = build_dir / f
                if fpath.exists():
                    shutil.move(str(fpath), str(pool_dir / f))
            for f in ["partition.yml", "checksums.sha256", "projects.json"]:
                fpath = build_dir / f
                if fpath.exists():
                    shutil.move(str(fpath), str(pool_dir / f))

            _flavour_progress(95, "Setting permissions")
            subprocess.run(["chown", "-R", "890:890", str(pool_dir)], check=True)

            _cleanup_build(build_dir, image_tag)

        _update_task_status(task_id, "completed", 100, "Build completed successfully")
        logger.info(f"Task {task_id}: Build completed for release {release_id}")

    except Exception as e:
        logger.error(f"Task {task_id}: Build failed: {e}")
        _update_task_status(task_id, "error", 0, str(e))
        try:
            _cleanup_build(build_dir, image_tag)
        except Exception:
            pass


def _cleanup_build(build_dir: Path, image_tag: str) -> None:
    subprocess.run(["docker", "rmi", "-f", image_tag], capture_output=True)
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)


def _mcs_worker():
    con = get_redis_connection()
    logger.info("MCS build worker started")
    while True:
        try:
            result = con.blpop(MCS_QUEUE_KEY, timeout=5)
            if result is None:
                continue
            _, task_data = result
            task = (
                json.loads(task_data)
                if isinstance(task_data, str)
                else json.loads(task_data.decode("utf-8"))
            )
            task_id = task.get("task_id", str(uuid.uuid4()))
            release_id = task.get("release_id")
            logger.info(f"MCS worker processing task {task_id}")
            _update_task_status(task_id, "queued", 0, "Task accepted, starting build")
            build_mcs_image(task_id, release_id)
        except Exception as e:
            logger.error(f"MCS worker error: {e}")
            time.sleep(1)


def start_mcs_worker():
    import asyncio

    def _run_worker():
        try:
            _mcs_worker()
        except Exception as e:
            logger.error(f"MCS worker crashed: {e}")

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _run_worker)
    logger.info("MCS build worker registered")

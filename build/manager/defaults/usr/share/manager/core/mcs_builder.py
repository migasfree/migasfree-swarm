import json
import logging
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256

import httpx
import yaml
from jinja2 import Environment, FileSystemLoader

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


def generate_dockerfile(project_data: dict, build_dir: Path) -> Path:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(MPI_TEMPLATE)
    base_os = project_data.get("base_os", "")
    if not base_os:
        raise ValueError("Project has no base_os defined")

    dockerfile_content = template.render(
        base_os=base_os,
        server=FQDN,
        project_slug=project_data.get("slug", str(project_data.get("id"))),
        project_name=project_data.get("name", ""),
        prefix=MCS_PREFIX,
    )

    dockerfile_path = build_dir / "Dockerfile"
    dockerfile_path.write_text(dockerfile_content)
    return dockerfile_path


def build_docker_image(
    build_dir: Path, image_tag: str, task_id: str | None = None
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
                if task_id:
                    _update_task_status(task_id, "building", 0, msg)
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
    image_name: str, container_name: str, root_dir: Path, task_id: str | None = None
) -> None:
    create = subprocess.run(
        ["docker", "create", "-h", "CI-MASTER", "--name", container_name, image_name],
        capture_output=True,
        text=True,
    )
    if create.returncode != 0:
        raise RuntimeError(f"Docker create failed: {create.stderr}")

    total_bytes = subprocess.run(
        ["docker", "image", "inspect", image_name, "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
    )
    total = int(total_bytes.stdout.strip()) if total_bytes.returncode == 0 else 0
    if total:
        logger.info(f"Image size: {total / (1024 * 1024):.0f} MiB")

    try:
        root_dir.mkdir(parents=True, exist_ok=True)
        export = subprocess.Popen(
            ["docker", "export", container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tar_proc = subprocess.Popen(
            ["tar", "-xf", "-", "-C", str(root_dir)],
            stdin=export.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        export.stdout.close()

        def monitor():
            while tar_proc.poll() is None:
                du = subprocess.run(
                    ["du", "-sb", str(root_dir)],
                    capture_output=True,
                    text=True,
                )
                if du.returncode == 0 and total > 0:
                    extracted = int(du.stdout.split()[0])
                    pct = min(extracted * 100 // total, 99)
                    _update_task_status(
                        task_id,
                        "exporting",
                        pct,
                        f"Extracting: {pct}% ({extracted // (1024 * 1024)} MiB)",
                    )
                time.sleep(3)

        t = threading.Thread(target=monitor, daemon=True)
        t.start()

        _, tar_err = tar_proc.communicate()
        _, export_err = export.communicate()
        t.join(timeout=1)
        if tar_proc.returncode != 0:
            raise RuntimeError(f"Tar extract failed: {tar_err.decode()}")
        if export.returncode != 0:
            raise RuntimeError(f"Docker export failed: {export_err.decode()}")
    finally:
        subprocess.run(["docker", "rm", container_name], capture_output=True)
    logger.info(f"Container exported and extracted to {root_dir}")


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


def get_partition_definition() -> str:
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


def generate_partition_yml(output_dir: Path) -> Path:
    yml_path = output_dir / "partition.yml"
    yml_path.write_text(get_partition_definition())
    return yml_path


def generate_checksums(output_dir: Path) -> Path:
    checksum_path = output_dir / "checksums.sha256"
    partition_def = yaml.safe_load(get_partition_definition())
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


def build_mcs_image(task_id: str, project_id: int):
    _update_task_status(task_id, "fetching", 0, "Fetching project data from Core API")
    try:
        project_data = _get_project_from_core(project_id)
    except Exception as e:
        _update_task_status(task_id, "error", 0, str(e))
        return

    slug = project_data.get("slug", str(project_id))
    build_dir = MCS_TEMP_DIR / f"{slug}-{task_id[:8]}"
    image_tag = f"mcs/{slug}:{task_id[:8]}"
    container_name = f"mcs-{slug}-{task_id[:8]}"
    root_dir = build_dir / "root"

    try:
        build_dir.mkdir(parents=True, exist_ok=True)

        _update_task_status(task_id, "building", 5, "Generating Dockerfile")
        generate_dockerfile(project_data, build_dir)

        _update_task_status(task_id, "building", 15, "Building Docker image")
        build_docker_image(build_dir, image_tag, task_id)

        _update_task_status(
            task_id, "exporting", 35, "Exporting and extracting root filesystem"
        )
        export_and_extract(image_tag, container_name, root_dir, task_id)

        partition_def = yaml.safe_load(get_partition_definition())
        excluded = {"BIOS", "EFI", "SWAP"}
        raw_partitions = [
            p for p in partition_def.get("partitions", []) if p["name"] not in excluded
        ]
        pool_dir = MCS_POOL_DIR / slug

        for part in raw_partitions:
            name = part["name"]
            raw_path = build_dir / f"{name}.raw"
            source_dir = root_dir / part["mount"].lstrip("/")
            if not source_dir.exists():
                source_dir.mkdir(parents=True, exist_ok=True)

            # Ensure boot directories exist for SYSTEM partition
            # so rescue can install GRUB and generate initramfs
            if name == "SYSTEM":
                (source_dir / "boot" / "grub").mkdir(parents=True, exist_ok=True)
                (source_dir / "boot" / "efi").mkdir(parents=True, exist_ok=True)

            # SYSTEM needs 128 MiB headroom for grub (~15M) + initramfs (~80M)
            headroom = 128 if name == "SYSTEM" else 8
            _update_task_status(task_id, "creating", 55, f"Creating {name}.raw")
            _create_ext4_image_from_dir(source_dir, raw_path, headroom_mb=headroom)

        _update_task_status(task_id, "finalizing", 80, "Generating metadata")
        generate_partition_yml(build_dir)
        generate_checksums(build_dir)
        update_projects_json(build_dir, slug, project_data)

        _update_task_status(task_id, "finalizing", 90, "Moving files to pool directory")
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

        _update_task_status(task_id, "completed", 100, "Build completed successfully")
        logger.info(f"Task {task_id}: Build completed for project {slug}")

    except Exception as e:
        logger.error(f"Task {task_id}: Build failed: {e}")
        _update_task_status(task_id, "error", 0, str(e))
    finally:
        _cleanup_build(build_dir, image_tag)


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
            project_id = task.get("project_id")
            logger.info(f"MCS worker processing task {task_id}")
            _update_task_status(task_id, "queued", 0, "Task accepted, starting build")
            build_mcs_image(task_id, project_id)
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

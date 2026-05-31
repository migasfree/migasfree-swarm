import json
import logging
import re
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone

from core.redis import get_redis_connection
from core.config import (
    FQDN,
    FQDN_IP,
    STACK,
    PATH_DATASHARES,
    HOST_VOLUME_BASE,
    HOST_STACK_DIR,
    get_dns_servers,
    HTTP_PROXY,
    HTTPS_PROXY,
    NO_PROXY,
)

logger = logging.getLogger(__name__)

MCS_QUEUE_KEY = "mcs:build_queue"
MCS_TASK_PREFIX = "mcs:task:"


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


def _is_safe_string(val: str | None) -> bool:
    if not val:
        return True
    return bool(re.match(r"^[a-zA-Z0-9_.-]*$", val))


def build_mcs_iso(task_id: str, server_url: str | None, server_ip: str | None, keymap: str | None):
    # Fallback to configured FQDN and FQDN_IP if not explicitly provided
    url = server_url if server_url else FQDN
    ip = server_ip if server_ip else FQDN_IP
    kmap = keymap if keymap else "es"

    # Security validation to avoid shell injection
    if not (_is_safe_string(url) and _is_safe_string(ip) and _is_safe_string(kmap)):
        raise ValueError("Invalid characters in parameters. Only alphanumeric, dots, dashes, and underscores allowed.")

    logger.info(f"Task {task_id}: Initializing MCS build with SERVER_URL={url}, SERVER_IP={ip}, KEYMAP={kmap}")
    _update_task_status(task_id, "initializing", 5, "Initializing workspace...")

    # Shared temporary path inside this container
    build_dir = PATH_DATASHARES / STACK / "tmp" / f"mcs-build-{task_id}"
    build_dir.mkdir(parents=True, exist_ok=True)

    try:

        dns_list = get_dns_servers()
        dns_flags = " ".join([f"--dns {d}" for d in dns_list])

        proxy_build_args = ""
        proxy_env_args = ""
        if HTTP_PROXY:
            proxy_build_args += f" --build-arg http_proxy={HTTP_PROXY} --build-arg HTTP_PROXY={HTTP_PROXY}"
            proxy_env_args += f" -e http_proxy={HTTP_PROXY} -e HTTP_PROXY={HTTP_PROXY}"
        if HTTPS_PROXY:
            proxy_build_args += f" --build-arg https_proxy={HTTPS_PROXY} --build-arg HTTPS_PROXY={HTTPS_PROXY}"
            proxy_env_args += f" -e https_proxy={HTTPS_PROXY} -e HTTPS_PROXY={HTTPS_PROXY}"
        if NO_PROXY:
            proxy_build_args += f" --build-arg no_proxy={NO_PROXY} --build-arg NO_PROXY={NO_PROXY}"
            proxy_env_args += f" -e no_proxy={NO_PROXY} -e NO_PROXY={NO_PROXY}"

        patch_cmds = ""
        if dns_flags:
            patch_cmds += f"sed -i 's/docker run /docker run {dns_flags} /g' scripts/build.sh && "
        if proxy_build_args:
            patch_cmds += f"sed -i 's/docker build /docker build {proxy_build_args} /g' scripts/build.sh && "
        if proxy_env_args:
            patch_cmds += f"sed -i 's/docker run /docker run {proxy_env_args} /g' scripts/build.sh && "

        # Construct dynamic sibling container shell commands
        shell_cmd = (
            f"apk add --no-cache git make parted bash rsync docker-cli sudo e2fsprogs dosfstools && "
            f"git clone https://github.com/migasfree/migasfree-clone-system.git . && "
            f"sed -i 's/docker run -ti/docker run/g' scripts/build.sh && "
            f"sed -i 's/losetup -D/losetup -d/g' scripts/build.sh && "
            f"{patch_cmds}"
            f"echo 'SERVER_URL=\"{url}\"' > mcs.conf && "
            f"echo 'SERVER_IP=\"{ip}\"' >> mcs.conf && "
            f"echo 'KEYMAP=\"{kmap}\"' >> mcs.conf && "
            f"echo 'MCS_SIZE_MB=\"3072\"' >> mcs.conf && "
            f"make build && "
            f"mkdir -p {str(HOST_STACK_DIR)}/pool/mcs && "
            f"cp artifacts/*.iso {str(HOST_STACK_DIR)}/pool/mcs/ && "
            f"chown -R 890:890 {str(HOST_STACK_DIR)}/pool/mcs && "
            f"chmod 755 {str(HOST_STACK_DIR)}/pool/mcs && "
            f"chmod 644 {str(HOST_STACK_DIR)}/pool/mcs/*.iso"
        )

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--privileged",
        ]

        for dns in dns_list:
            docker_cmd += ["--dns", dns]

        if HTTP_PROXY:
            docker_cmd += ["-e", f"http_proxy={HTTP_PROXY}", "-e", f"HTTP_PROXY={HTTP_PROXY}"]
        if HTTPS_PROXY:
            docker_cmd += ["-e", f"https_proxy={HTTPS_PROXY}", "-e", f"HTTPS_PROXY={HTTPS_PROXY}"]
        if NO_PROXY:
            docker_cmd += ["-e", f"no_proxy={NO_PROXY}", "-e", f"NO_PROXY={NO_PROXY}"]

        docker_cmd += [
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
            "-v",
            "/dev:/dev",
            "-v",
            f"{str(HOST_VOLUME_BASE)}:{str(HOST_VOLUME_BASE)}",
            "-w",
            f"{str(HOST_STACK_DIR)}/tmp/mcs-build-{task_id}",
            "alpine:3.22",
            "/bin/sh",
            "-c",
            shell_cmd
        ]

        logger.info(f"Task {task_id}: Launching builder container...")
        _update_task_status(task_id, "starting container", 10, "Launching build environment container...")

        proc = subprocess.Popen(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        make_build_started = False
        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip()
            if not line:
                continue
            logger.info(f"Task {task_id} log: {line}")

            if "make build" in line.lower() or "sudo ./scripts/build.sh" in line.lower():
                make_build_started = True

            # Smart progress updates based on output
            if not make_build_started and "fetch" in line.lower() and "apk" in line.lower():
                _update_task_status(task_id, "installing dependencies", 15, "Installing Alpine build packages...")
            elif not make_build_started and "cloning into" in line.lower():
                _update_task_status(task_id, "cloning repository", 25, "Cloning MCS system repository...")
            elif "creando" in line.lower() and ".img" in line.lower():
                _update_task_status(task_id, "allocating image", 35, "Creating raw virtual disk image...")
            elif "docker build" in line.lower() or "step " in line.lower():
                _update_task_status(task_id, "building container", 55, "Building isolated MCS filesystem...")
            elif "formateando" in line.lower() or "format partitions" in line.lower():
                _update_task_status(task_id, "formatting partitions", 75, "Formatting partitions...")
            elif "instalando paquetes" in line.lower() or "installing core os" in line.lower():
                _update_task_status(task_id, "installing system", 85, "Installing core OS packages...")
            elif "installing grub" in line.lower() or "installing bootloader" in line.lower():
                _update_task_status(task_id, "installing bootloader", 90, "Installing GRUB bootloader...")
            elif "finalizing" in line.lower() or "bootable iso" in line.lower():
                _update_task_status(task_id, "finalizing", 95, "Finalizing bootable ISO package...")

        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError(f"Build container exited with non-zero code {proc.returncode}")

        # Double check if file exists in pool
        mcs_pool_dir = PATH_DATASHARES / STACK / "pool" / "mcs"
        iso_files = list(mcs_pool_dir.glob("*.iso"))
        if not iso_files:
            raise RuntimeError("Build finished, but no .iso file was found in the pool directory.")

        _update_task_status(task_id, "completed", 100, "MCS bootable ISO created successfully!")
        logger.info(f"Task {task_id}: Build completed successfully.")

    except Exception as e:
        logger.error(f"Task {task_id}: Build failed: {e}")
        _update_task_status(task_id, "error", 0, f"Build failed: {str(e)}")
    finally:
        # Always clean up temporary workspace inside /tmp
        logger.info(f"Task {task_id}: Cleaning up build workspace...")
        shutil.rmtree(build_dir, ignore_errors=True)


def _mcs_worker():
    con = get_redis_connection()
    logger.info("MCS ISO build worker started")
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
            server_url = task.get("server_url")
            server_ip = task.get("server_ip")
            keymap = task.get("keymap")

            logger.info(f"MCS worker processing task {task_id}")
            _update_task_status(task_id, "queued", 0, "Task accepted, starting build process")
            build_mcs_iso(task_id, server_url, server_ip, keymap)
        except Exception as e:
            logger.error(f"MCS worker error: {e}")
            time.sleep(5)
            try:
                con = get_redis_connection()
            except Exception:
                pass


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

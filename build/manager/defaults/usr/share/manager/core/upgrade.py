import os
import re
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# Microservices that make up a migasfree-swarm stack (same list as pull.sh)
MIGASFREE_SERVICES = [
    "swarm", "proxy", "certbot", "datashare_console", "datastore",
    "datastore_console", "database", "database_console", "core",
    "console", "public", "worker_console", "tunnel", "mcp-server",
    "pms-apt", "pms-yum", "pms-pacman", "pms-apk", "pms-wpt",
]

CHECK_URL = "https://migasfree.org/pub/install-swarm"
CHECK_INTERVAL_SECONDS = 6 * 3600  # 6 hours
CHECK_TIMEOUT_SECONDS = 15
VERSION_REGEX = re.compile(r'_VERSION="([^"]+)"')


@dataclass
class VersionStatus:
    current_version: str = ""
    latest_version: str = ""
    has_update: bool = False
    last_checked: str = ""
    error: str = ""


_status = VersionStatus()
_check_task: asyncio.Task | None = None


def get_version_status() -> VersionStatus:
    """Return the current cached version status."""
    return _status


def are_images_downloaded(version: str) -> bool:
    """Check if all images for the target version are available in the local docker daemon."""
    if not version:
        return False
    try:
        import docker
        client = docker.from_env()
        existing_tags = set()
        for img in client.images.list():
            if img.tags:
                existing_tags.update(img.tags)

        required_images = get_image_list(version)
        for req in required_images:
            if not any(req in tag for tag in existing_tags):
                return False
        return True
    except Exception as e:
        logger.warning(f"Could not check local docker images: {e}")
        return False


def get_image_list(version: str) -> list[str]:
    """Return the full list of Docker image tags for a given version."""
    return [f"migasfree/{svc}:{version}" for svc in MIGASFREE_SERVICES]


async def check_latest_version() -> None:
    """Fetch the install-swarm script and extract _VERSION."""
    global _status

    current = os.environ.get("TAG", "")
    _status.current_version = current

    try:
        async with httpx.AsyncClient(
            timeout=CHECK_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            response = await client.get(CHECK_URL)
            response.raise_for_status()

        match = VERSION_REGEX.search(response.text)
        if match:
            latest = match.group(1)
            _status.latest_version = latest
            _status.has_update = latest != current
            _status.error = ""
        else:
            _status.error = "Could not parse _VERSION from install-swarm"
            logger.warning(_status.error)

    except httpx.HTTPError as e:
        _status.error = f"HTTP error checking for updates: {e}"
        logger.warning(_status.error)
    except Exception as e:
        _status.error = f"Unexpected error checking for updates: {e}"
        logger.warning(_status.error)

    _status.last_checked = datetime.now(timezone.utc).isoformat()

    if _status.has_update:
        logger.info(
            f"New version available: {_status.latest_version} "
            f"(current: {_status.current_version})"
        )
    else:
        logger.debug(
            f"Version check complete: current={_status.current_version}, "
            f"latest={_status.latest_version}"
        )


async def _periodic_check_loop() -> None:
    """Background loop that checks for updates periodically."""
    # Initial check on startup (small delay to let other services start)
    await asyncio.sleep(10)
    await check_latest_version()

    while True:
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        await check_latest_version()


def start_version_checker() -> None:
    """Start the periodic version checker as a background task."""
    global _check_task
    if _check_task is None or _check_task.done():
        _check_task = asyncio.create_task(_periodic_check_loop())
        logger.info(
            f"Version checker started (interval: {CHECK_INTERVAL_SECONDS}s)"
        )


def stop_version_checker() -> None:
    """Cancel the periodic version checker."""
    global _check_task
    if _check_task and not _check_task.done():
        _check_task.cancel()
        logger.info("Version checker stopped")

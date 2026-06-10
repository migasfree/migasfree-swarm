import json
import logging
import uuid
from datetime import datetime, timezone
import httpx
import subprocess

from fastapi import APIRouter, Depends, HTTPException, status

from core.config import API_VERSION, MGI_POOL_DIR, CORE_TOKEN_URL
from core.models import BuildMGImageRequest, BuildMGImageResponse, BuildTaskStatus
from core.core_client import get_current_superuser, get_cached_token
from core.redis import get_redis_connection

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_VERSION}/internal/mgi",
    tags=["mgi"],
)

MGI_QUEUE_KEY = "mgi:build_queue"
MGI_TASK_PREFIX = "mgi:task:"


@router.post("/build", response_model=BuildMGImageResponse)
async def build_mgi_image(
    request: BuildMGImageRequest,
    _: dict = Depends(get_current_superuser),
):
    release_id = request.release_id
    task_id = str(uuid.uuid4())

    con = get_redis_connection()
    task_data = {
        "task_id": task_id,
        "release_id": release_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    con.rpush(MGI_QUEUE_KEY, json.dumps(task_data))

    con.hset(
        f"{MGI_TASK_PREFIX}{task_id}",
        mapping={
            "status": "queued",
            "progress": "0",
            "message": "Task queued",
            "created_at": task_data["created_at"],
            "updated_at": task_data["created_at"],
        },
    )
    con.expire(f"{MGI_TASK_PREFIX}{task_id}", 86400)

    logger.info(f"MGI build task {task_id} queued for release {release_id}")
    return BuildMGImageResponse(task_id=task_id)


@router.get("/build/{task_id}/status", response_model=BuildTaskStatus)
async def get_build_status(task_id: str):
    con = get_redis_connection()
    key = f"{MGI_TASK_PREFIX}{task_id}"
    data = con.hgetall(key)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    return BuildTaskStatus(
        task_id=task_id,
        status=data.get("status", "unknown"),
        progress=int(data.get("progress", 0)),
        message=data.get("message", ""),
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )


async def _get_mpi_name_from_build(build_id: str) -> str:
    token = get_cached_token()
    headers = {"accept": "application/json", "Authorization": f"Token {token}"}
    core_api_url = CORE_TOKEN_URL.replace("/token", "")

    async with httpx.AsyncClient() as client:
        # 1. Fetch build record
        build_resp = await client.get(
            f"{core_api_url}/token/mgi/build/{build_id}/",
            headers=headers,
            follow_redirects=False,
        )
        if build_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Build record {build_id} not found in Core database"
            )
        build_data = build_resp.json()

        # Check build status
        if build_data.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Build {build_id} status is '{build_data.get('status')}'. Only completed builds can be promoted/demoted."
            )

        release_id = build_data.get("release")
        flavour_id = build_data.get("flavour")
        
        if not release_id or not flavour_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Build record lacks release or flavour relation"
            )

        # 2. Fetch release
        release_resp = await client.get(
            f"{core_api_url}/token/mgi/release/{release_id}/",
            headers=headers,
            follow_redirects=False,
        )
        if release_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Release {release_id} not found"
            )
        release_data = release_resp.json()

        # 3. Fetch config to get project_id
        config_id = release_data.get("config")
        if isinstance(config_id, dict):
            config_id = config_id["id"]
        config_resp = await client.get(
            f"{core_api_url}/token/mgi/config/{config_id}/",
            headers=headers,
            follow_redirects=False,
        )
        if config_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config {config_id} not found"
            )
        config_data = config_resp.json()

        # 4. Fetch project
        project_id = config_data.get("project")
        if isinstance(project_id, dict):
            project_id = project_id["id"]
        project_resp = await client.get(
            f"{core_api_url}/token/projects/{project_id}/",
            headers=headers,
            follow_redirects=False,
        )
        if project_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        project_data = project_resp.json()

        # 5. Fetch flavour
        flavour_resp = await client.get(
            f"{core_api_url}/token/mgi/flavour/{flavour_id}/",
            headers=headers,
            follow_redirects=False,
        )
        if flavour_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flavour {flavour_id} not found"
            )
        flavour_data = flavour_resp.json()

    slug = project_data.get("slug", str(project_id))
    mpi_name = f"{project_data.get('name', slug)}-{release_data['name']}-{flavour_data['name']}".lower()
    return mpi_name


def _update_catalog_status(mpi_name: str, enabled: bool, build_id: int = None) -> None:
    catalog_path = MGI_POOL_DIR / "catalog.json"
    if not catalog_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catalog file not found on disk"
        )

    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Error reading catalog.json: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read catalog file: {str(e)}"
        )

    if not isinstance(catalog, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Catalog file has an invalid format (not a list)"
        )

    entry_found = False
    for entry in catalog:
        if isinstance(entry, dict) and entry.get("name") == mpi_name:
            entry["enabled"] = enabled
            if build_id is not None:
                entry["build_id"] = build_id
            entry_found = True
            break

    if not entry_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image name '{mpi_name}' not found in the catalog. Generate a build first."
        )

    try:
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["chown", "890:890", str(catalog_path)], check=True)
    except Exception as e:
        logger.error(f"Failed to save catalog.json: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save catalog file: {str(e)}"
        )


@router.post("/builds/{build_id}/promote")
async def promote_mgi_build(
    build_id: str,
    _: dict = Depends(get_current_superuser),
):
    """
    Promote an MGI image by setting 'enabled': True in the catalog.json
    based on its completed Core build_id.
    """
    mpi_name = await _get_mpi_name_from_build(build_id)
    _update_catalog_status(mpi_name, enabled=True, build_id=int(build_id))
    logger.info(f"Successfully promoted build {build_id} (image: {mpi_name})")
    return {"status": "success", "message": f"Image '{mpi_name}' promoted successfully"}


@router.post("/builds/{build_id}/demote")
async def demote_mgi_build(
    build_id: str,
    _: dict = Depends(get_current_superuser),
):
    """
    Demote an MGI image by setting 'enabled': False in the catalog.json
    based on its completed Core build_id.
    """
    mpi_name = await _get_mpi_name_from_build(build_id)
    _update_catalog_status(mpi_name, enabled=False, build_id=int(build_id))
    logger.info(f"Successfully demoted build {build_id} (image: {mpi_name})")
    return {"status": "success", "message": f"Image '{mpi_name}' demoted successfully"}

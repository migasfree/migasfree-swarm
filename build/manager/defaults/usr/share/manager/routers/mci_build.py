import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from core.config import API_VERSION
from core.models import BuildMCImageRequest, BuildMCImageResponse, BuildTaskStatus
from core.core_client import get_current_superuser
from core.redis import get_redis_connection

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_VERSION}/private/mci",
    tags=["mci"],
)

MCI_QUEUE_KEY = "mci:build_queue"
MCI_TASK_PREFIX = "mci:task:"


@router.post("/build", response_model=BuildMCImageResponse)
async def build_mci_image(
    request: BuildMCImageRequest,
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
    con.rpush(MCI_QUEUE_KEY, json.dumps(task_data))

    con.hset(
        f"{MCI_TASK_PREFIX}{task_id}",
        mapping={
            "status": "queued",
            "progress": "0",
            "message": "Task queued",
            "created_at": task_data["created_at"],
            "updated_at": task_data["created_at"],
        },
    )
    con.expire(f"{MCI_TASK_PREFIX}{task_id}", 86400)

    logger.info(f"MCI build task {task_id} queued for release {release_id}")
    return BuildMCImageResponse(task_id=task_id)


@router.get("/build/{task_id}/status", response_model=BuildTaskStatus)
async def get_build_status(task_id: str):
    con = get_redis_connection()
    key = f"{MCI_TASK_PREFIX}{task_id}"
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

import json
import logging
import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from sse_starlette.sse import EventSourceResponse

from core.config import API_VERSION
from core.upgrade import (
    get_version_status,
    check_latest_version,
    are_images_downloaded,
)
from core.portainer import (
    authenticate,
    pull_images_on_all_nodes,
    PullProgress,
)

logger = logging.getLogger(__name__)

router_private = APIRouter(
    prefix=f"{API_VERSION}/private",
    tags=["upgrade"],
)

# Shared state for the pull operation
_pull_in_progress = False
_pull_events: asyncio.Queue | None = None


class PullRequest(BaseModel):
    username: str
    password: str
    version: str | None = None  # If None, uses latest detected version


# ─── Version status ────────────────────────────────────────────────


@router_private.get("/version/status")
async def version_status():
    """Returns current and latest version info."""
    vs = get_version_status()
    images_downloaded = are_images_downloaded(vs.latest_version) if vs.latest_version else False
    has_notification = vs.has_update or not images_downloaded
    return JSONResponse(content={
        "current_version": vs.current_version,
        "latest_version": vs.latest_version,
        "has_update": vs.has_update,
        "images_downloaded": images_downloaded,
        "has_notification": has_notification,
        "last_checked": vs.last_checked,
        "error": vs.error,
        "pull_in_progress": _pull_in_progress,
    })


@router_private.post("/version/check")
async def version_check():
    """Force an immediate version check."""
    await check_latest_version()
    vs = get_version_status()
    return JSONResponse(content={
        "current_version": vs.current_version,
        "latest_version": vs.latest_version,
        "has_update": vs.has_update,
        "last_checked": vs.last_checked,
    })


# ─── Image pull ────────────────────────────────────────────────────


@router_private.post("/images/pull")
async def images_pull(request: PullRequest):
    """
    Authenticate against Portainer and start pulling images for the
    target version on all Swarm nodes. Returns immediately; progress
    is streamed via the /images/pull/stream SSE endpoint.
    """
    global _pull_in_progress, _pull_events

    if _pull_in_progress:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pull operation is already in progress",
        )

    # Determine target version
    target_version = request.version
    if not target_version:
        vs = get_version_status()
        target_version = vs.latest_version
        if not target_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No target version specified and no latest version detected",
            )

    # Authenticate against Portainer
    try:
        session = await authenticate(request.username, request.password)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Portainer authentication failed: {e}",
        )

    # Start the pull in background
    _pull_events = asyncio.Queue()
    _pull_in_progress = True

    async def _run_pull():
        global _pull_in_progress
        try:
            async def progress_cb(progress: PullProgress):
                await _pull_events.put({
                    "event": "progress",
                    "data": {
                        "node": progress.node,
                        "image": progress.image,
                        "status": progress.status,
                        "detail": progress.detail,
                    },
                })

            summary = await pull_images_on_all_nodes(
                session=session,
                version=target_version,
                progress_callback=progress_cb,
            )

            await _pull_events.put({
                "event": "complete",
                "data": summary,
            })
        except Exception as e:
            logger.error(f"Pull operation failed: {e}", exc_info=True)
            await _pull_events.put({
                "event": "error",
                "data": {"error": str(e)},
            })
        finally:
            _pull_in_progress = False

    asyncio.create_task(_run_pull())

    return JSONResponse(content={
        "status": "started",
        "version": target_version,
        "message": "Pull operation started. Connect to /images/pull/stream for progress.",
    })


@router_private.get("/images/pull/stream")
async def images_pull_stream():
    """SSE endpoint streaming the progress of an ongoing image pull."""
    if _pull_events is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pull operation has been started",
        )

    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(_pull_events.get(), timeout=30)
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"]),
                }
                if event["event"] in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                yield {
                    "event": "ping",
                    "data": json.dumps({"keepalive": True}),
                }

    return EventSourceResponse(event_generator())

import os
import sys
import logging
import asyncio
import json
from collections import deque

from fastapi import APIRouter, Request, FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from sse_starlette.sse import EventSourceResponse

from core.config import API_VERSION
from core.status import Message
from core.utils import get_timestamp, get_organization
from core.monitor import DockerSwarmMonitor
from core.availability import start_recording, stop_recording, get_database_backends


FQDN = os.environ["FQDN"]
STACK = os.environ["STACK"]
TAG = os.environ["TAG"]

MESSAGES_LOG = deque(maxlen=500)


client_id_counter = 0
docker_monitor = None


# Logging configuration
logger = logging.getLogger("services")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


router = APIRouter(prefix="", tags=["status"])

router_internal = APIRouter(prefix=f"{API_VERSION}/internal", tags=["status"])

router_private = APIRouter(prefix=f"{API_VERSION}/private", tags=["status"])

router_public = APIRouter(prefix=f"{API_VERSION}/public", tags=["status"])

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global docker_monitor
    logger.info("Starting application...")
    docker_monitor = DockerSwarmMonitor()
    await docker_monitor.start()
    start_recording()
    logger.info("Application started successfully")
    yield
    logger.info("Shutting down application...")
    if docker_monitor:
        await docker_monitor.stop()
    await stop_recording()


@router_internal.post("/message")
async def post_message(message: Message):
    """Receives a message with the status of the process during the startup"""

    data = message.dict()
    data["timestamp"] = get_timestamp()
    MESSAGES_LOG.append(data)
    logger.debug("post_message data: %s", data)

    return JSONResponse(content={"status": "ok"})


@router_internal.get("/backends")
async def get_backends():
    """Returns database backends with Node IPs for pgpool"""
    try:
        backends = get_database_backends()
        return JSONResponse(content=backends)
    except Exception as e:
        logger.error(f"Error getting backends: {e}")
        return JSONResponse(content=[], status_code=500)


@router.get("/favicon.ico")
async def favicon():
    """Redirect to logo"""
    return RedirectResponse(url=f"https://{FQDN}/manager/static/img/logo.svg")


@router_private.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    """Status page"""
    cache_result = await docker_monitor.cache()
    context = {"services": cache_result, "request": request}
    return templates.TemplateResponse("status.html", context)


# SSE endpoint: manager stream
@router_private.get("/stream")
async def service_stream(request: Request):
    global client_id_counter
    queue = asyncio.Queue(maxsize=100)

    async with docker_monitor.client_id_lock:
        client_id = client_id_counter
        client_id_counter += 1
        docker_monitor.sse_clients[client_id] = queue

    logger.info(
        f"Service SSE client {client_id} connected. Total clients: {len(docker_monitor.sse_clients)}"
    )

    async def event_generator():
        try:
            # Send initial state from cache
            cache_result = await docker_monitor.cache()
            logger.info(
                f"Client {client_id}: Sending initial cache with {len(cache_result)} services"
            )

            for service_name, service_data in cache_result.items():
                # Build status object from cache - no filtering by 'nodes'
                status_obj = {
                    "status": service_data.get("status", "unknown"),
                    "running": service_data.get("nodes", 0),  # This is the count
                    "desired": 1,  # We don't store this in cache
                    "preparing": 0,
                    "failed": 0,
                    "mode": "replicated",
                    "nodes": service_data.get("node", "").split(", ")
                    if service_data.get("node")
                    else [],
                    "containers": service_data.get("container", "").split(", ")
                    if service_data.get("container")
                    else [],
                }

                initial_data = {
                    "service": service_name,
                    "status": status_obj,
                    "timestamp": get_timestamp(),
                }

                logger.debug(
                    f"Client {client_id}: Sending {service_name} = {status_obj['status']} ({status_obj['running']})"
                )
                yield {"event": "status", "data": json.dumps(initial_data)}

            # Send last 50 log messages
            log_count = len(list(MESSAGES_LOG)[-50:])
            logger.debug(f"Client {client_id}: Sending {log_count} log messages")
            for message in list(MESSAGES_LOG)[-50:]:
                yield {"event": "log", "data": json.dumps(message)}

            logger.info(
                f"Client {client_id}: Initial state sent, starting event stream"
            )

            # Stream updates
            while True:
                if await request.is_disconnected():
                    logger.info(f"Client {client_id}: Disconnected by request")
                    break

                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=30)
                    logger.debug(
                        f"Client {client_id}: Broadcasting {event_data['event']} event"
                    )
                    yield {
                        "event": event_data["event"],
                        "data": json.dumps(event_data["data"]),
                    }
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield {
                        "event": "ping",
                        "data": json.dumps({"timestamp": get_timestamp()}),
                    }
        except Exception as e:
            logger.error(
                f"Client {client_id}: Error in event_generator: {e}", exc_info=True
            )
        finally:
            async with docker_monitor.client_id_lock:
                docker_monitor.sse_clients.pop(client_id, None)
            logger.info(
                f"Client {client_id}: Disconnected. Remaining: {len(docker_monitor.sse_clients)}"
            )

    return EventSourceResponse(event_generator())


@router_private.get("/info")
async def get_info():
    """Get static application info (organization, stack, tag, disabled)"""
    disabled = []
    if os.environ["HTTPSMODE"] == "manual":
        disabled.append("certbot")

    return JSONResponse(
        content={
            "organization": await get_organization(STACK),
            "stack": STACK,
            "tag": TAG,
            "disabled": disabled,
        }
    )

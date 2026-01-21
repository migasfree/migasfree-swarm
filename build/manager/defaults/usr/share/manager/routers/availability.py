import logging
import re

from fastapi import APIRouter, Request, status as http_status
from fastapi.responses import JSONResponse

from core.availability import (
    increment_sync_attempt,
    is_server_saturated,
)
from core.redis import get_redis_connection
from core.config import SYNC_QUEUE_PROCESS_INTERVAL

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/public", tags=["availability"])


def get_uuid_from_header(client_dn: str) -> str | None:
    """
    Extracts the UUID from the X-SSL-Client-CN header.
    Format expected: /O=org/OU=unit/CN=UUID_CERT-ID
    """
    logger.debug("X-SSL-Client-CN header: %s", client_dn)
    try:
        cn_match = re.search(r"/CN=([^/]+)", client_dn)
        if not cn_match:
            raise ValueError("CN not found in DN")

        cn_value = cn_match.group(1)

        # Parse the CN format: UUID_CERT-ID
        parts = cn_value.rsplit("_", 1)
        if len(parts) != 2:
            raise ValueError("Invalid CN format")

        cert_uuid, _ = parts
        return cert_uuid
    except Exception as e:
        logger.error(f"Error parsing client DN: {e}")
        return None


@router.api_route("/synchronizations/availability/", methods=["POST"])
async def check_availability(request: Request):
    """
    Endpoint to check server saturation before syncing.
    """
    increment_sync_attempt()

    if not is_server_saturated():
        return JSONResponse({"status": "ok"}, status_code=http_status.HTTP_200_OK)

    # Server is saturated
    logger.info("Server is saturated, queuing request")

    client_dn = request.headers.get("x-ssl-client-cn")
    if client_dn:
        try:
            cert_uuid = get_uuid_from_header(client_dn)
            if cert_uuid:
                con = get_redis_connection()
                queue_items = con.lrange("manager:sync_queue", 0, -1)

                if cert_uuid not in queue_items:
                    con.rpush("manager:sync_queue", cert_uuid)
                    logger.info(f"Queued UUID: {cert_uuid}")
                else:
                    logger.info(f"UUID already in queue: {cert_uuid}")
        except Exception as e:
            logger.error(f"Error processing mTLS header or pushing to Redis queue: {e}")
    else:
        logger.debug("No X-SSL-Client-CN header, skipping mTLS verification")

    retry_after = int(SYNC_QUEUE_PROCESS_INTERVAL) * 5
    return JSONResponse(
        content={"status": "saturated", "retry_after": retry_after},
        status_code=http_status.HTTP_429_TOO_MANY_REQUESTS,
    )

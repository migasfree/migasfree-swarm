import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.availability import (
    get_saturation_metrics,
    get_sync_attempts,
    get_metrics_from_history,
)
from core.config import (
    SYNC_MAX_DB_LATENCY,
    SYNC_MAX_CORE_LOAD,
    METRICS_RECORDING_INTERVAL,
)

logger = logging.getLogger(__name__)


router_private = APIRouter(prefix="/v1/private", tags=["metrics"])

templates = Jinja2Templates(directory="/usr/share/manager/templates")


@router_private.get("/metrics/json")
async def metrics_json():
    """
    Return metrics in JSON format for the dashboard.
    """
    current = get_saturation_metrics()
    history = get_metrics_from_history()

    # Normalize current to match history structure if needed, or just send as is
    # Add attempts to 'current' snapshot
    current["attempts"] = get_sync_attempts()

    data = {
        "current": current,
        "history": history,
        "limits": {
            "db_latency": SYNC_MAX_DB_LATENCY,
            "core_cpu": SYNC_MAX_CORE_LOAD,
            "recording_interval": METRICS_RECORDING_INTERVAL,
        },
    }
    return data


@router_private.get("/metrics/dashboard", response_class=HTMLResponse)
async def metrics_dashboard(request: Request):
    """
    Render metrics dashboard.
    """
    return templates.TemplateResponse("metrics.html", {"request": request})

"""
System, Health and Status Endpoints
"""
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import tda_worker
from core.auth import get_core_staff_user

logger = logging.getLogger("migasfree-tda")
router = APIRouter()


@router.get("/health")
@router.get("/api/v1/health")
async def health():
    """Liveness probe for Docker container healthcheck."""
    return JSONResponse(content={"status": "healthy"})


@router.get("/api/v1/status")
async def get_status(user: dict = Depends(get_core_staff_user)):
    """Return the current processing status of the TDA engine."""
    return JSONResponse(content=tda_worker.get_status())

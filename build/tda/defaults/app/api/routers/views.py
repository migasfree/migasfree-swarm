"""
HTML Views Endpoints (Jinja2 Templates)
"""
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.config import APP_DIR

router = APIRouter(tags=["views"])
templates = Jinja2Templates(directory=os.path.join(APP_DIR, "templates"))


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def tda_dashboard(request: Request):
    """Render the main interactive TDA Dashboard."""
    lenses_env = os.getenv("TDA_LENSES", "health,obsolescence,software,migration,sync,diversity")
    configured_lenses = [l.strip() for l in lenses_env.split(",") if l.strip()]
    return templates.TemplateResponse(
        request,
        "tda.html",
        {"configured_lenses": configured_lenses}
    )


@router.get("/settings", response_class=HTMLResponse)
async def tda_settings(request: Request):
    """Render the TDA settings/configuration page."""
    lenses_env = os.getenv("TDA_LENSES", "health,obsolescence,software,migration,sync,diversity")
    configured_lenses = [l.strip() for l in lenses_env.split(",") if l.strip()]
    return templates.TemplateResponse(
        request,
        "tda_settings.html",
        {"configured_lenses": configured_lenses}
    )

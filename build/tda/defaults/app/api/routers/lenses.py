"""
Lens Management and Graph Endpoints
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Response
from fastapi.responses import JSONResponse, HTMLResponse
from core.config import TDA_DIR, logger
from core.auth import get_core_staff_user
from api.models import LensSpec
import tda_worker

from lens_store import (
    load_all_lenses,
    load_lens,
    save_lens,
    delete_lens,
    has_lens_output,
    legacy_output_path,
    lens_output_path,
    LENS_TYPE_LABELS,
)

router = APIRouter(tags=["lenses"])


def _available_lens_names() -> set:
    """Lens names with a generated graph (self-contained folder or legacy path)."""
    available = set()
    if not os.path.exists(TDA_DIR):
        return available
    try:
        for spec in load_all_lenses():
            name = spec["name"]
            if has_lens_output(name, "json") or os.path.isfile(legacy_output_path(name, "json")):
                available.add(name)
    except Exception:
        pass
    return available


def _resolve_lens_file(lens_name: str, ext: str) -> str:
    """Path of a lens output, preferring the self-contained folder."""
    new_path = lens_output_path(lens_name, ext)
    if os.path.isfile(new_path):
        return new_path
    return legacy_output_path(lens_name, ext)


@router.post("/api/v1/recalculate")
async def trigger_recalculate(
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_core_staff_user)
):
    """
    Trigger an on-demand TDA recalculation run in background.
    Requires Staff or Superuser authentication.
    """
    current_status = tda_worker.get_status()
    if current_status.get("is_running"):
        return JSONResponse(
            status_code=409,
            content={"message": "Analysis already in progress", "status": current_status}
        )

    background_tasks.add_task(tda_worker.run_analysis)
    return JSONResponse(
        status_code=202,
        content={"message": "Recalculation started in background", "status": "started"}
    )


@router.get("/api/v1/lenses")
async def get_lenses(user: dict = Depends(get_core_staff_user)):
    """Return the names of the lenses with generated graphs (from the lens store)."""
    try:
        available_names = _available_lens_names()
        available_lenses = [
            spec["name"] for spec in load_all_lenses() if spec["name"] in available_names
        ]
        return JSONResponse(content=available_lenses)
    except Exception as e:
        logger.error(f"Error listing lenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/lenses/details")
async def get_lens_details(user: dict = Depends(get_core_staff_user)):
    """Return all lens descriptors (built-in + custom) with generation status."""
    try:
        available_names = _available_lens_names()
        specs = load_all_lenses()
        for spec in specs:
            spec["generated"] = spec["name"] in available_names
            lens_type = (spec.get("lens") or {}).get("type", "pca")
            spec["projection_label"] = LENS_TYPE_LABELS.get(lens_type, lens_type)
        return JSONResponse(content=specs)
    except Exception as e:
        logger.error(f"Error listing lens details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/lenses/{lens_name}")
async def get_lens(lens_name: str, user: dict = Depends(get_core_staff_user)):
    """Return a single lens descriptor."""
    spec = load_lens(lens_name)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Lens '{lens_name}' not found")
    lens_type = (spec.get("lens") or {}).get("type", "pca")
    spec["projection_label"] = LENS_TYPE_LABELS.get(lens_type, lens_type)
    return JSONResponse(content=spec)


@router.post("/api/v1/lenses")
async def create_lens(spec: LensSpec, user: dict = Depends(get_core_staff_user)):
    """Create a new user-defined lens."""
    try:
        descriptor = spec.to_descriptor()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if load_lens(descriptor["name"]) is not None:
        raise HTTPException(status_code=409, detail=f"Lens '{descriptor['name']}' already exists")
    try:
        save_lens(descriptor)
    except Exception as e:
        logger.error(f"Error saving lens '{descriptor['name']}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
    logger.info(f"Lens '{descriptor['name']}' created by {user.get('username', '?')}")
    return JSONResponse(status_code=201, content=descriptor)


@router.put("/api/v1/lenses/{lens_name}")
async def update_lens(lens_name: str, spec: LensSpec, user: dict = Depends(get_core_staff_user)):
    """Update a lens descriptor (name immutable for built-in lenses)."""
    existing = load_lens(lens_name)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Lens '{lens_name}' not found")
    if existing.get("builtin") and not spec.builtin:
        spec.builtin = True
    try:
        descriptor = spec.to_descriptor(current_name=lens_name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    try:
        save_lens(descriptor)
    except Exception as e:
        logger.error(f"Error updating lens '{lens_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
    logger.info(f"Lens '{lens_name}' updated by {user.get('username', '?')}")
    return JSONResponse(content=descriptor)


@router.delete("/api/v1/lenses/{lens_name}")
async def remove_lens(lens_name: str, user: dict = Depends(get_core_staff_user)):
    """Delete a lens."""
    try:
        delete_lens(lens_name)
    except ValueError as e:
        if str(e).startswith("Lens '") and "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    logger.info(f"Lens '{lens_name}' deleted by {user.get('username', '?')}")
    return JSONResponse(content={"status": "deleted", "name": lens_name})


@router.post("/api/v1/lenses/{lens_name}/recalculate")
async def recalculate_lens(
    lens_name: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_core_staff_user),
):
    """
    Recalculate a single lens in the background.
    Requires Staff or Superuser authentication.
    """
    if load_lens(lens_name) is None:
        raise HTTPException(status_code=404, detail=f"Lens '{lens_name}' not found")
    current_status = tda_worker.get_status()
    if current_status.get("is_running"):
        return JSONResponse(
            status_code=409,
            content={"message": "Analysis already in progress", "status": current_status}
        )

    background_tasks.add_task(tda_worker.run_analysis, only_lens=lens_name)
    return JSONResponse(
        status_code=202,
        content={"message": f"Recalculation of lens '{lens_name}' started in background", "status": "started"}
    )


@router.get("/api/v1/lens/{lens_name}/json")
async def get_lens_json(lens_name: str, user: dict = Depends(get_core_staff_user)):
    """Return the JSON graph representation for a given lens."""
    json_path = _resolve_lens_file(lens_name, "json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail=f"Lens '{lens_name}' not found")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content=content, media_type="application/json")
    except Exception as e:
        logger.error(f"Error reading JSON for lens {lens_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/lens/{lens_name}/html")
async def get_lens_html(lens_name: str, user: dict = Depends(get_core_staff_user)):
    """Return the KeplerMapper diagnostic HTML visualization."""
    html_path = _resolve_lens_file(lens_name, "html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail=f"Lens HTML for '{lens_name}' not found")

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        html_content = html_content.replace(
            '#display {\n  color: #95A5A6;\n  background: #212121;\n}',
            '#display {\n  color: #222;\n  background: #fff;\n}'
        ).replace(
            '#header {\n  background: #111111;\n}',
            '#header {\n  background: #f8f9fa;\n  border-bottom: 1px solid #dee2e6;\n  color: #222;\n}'
        ).replace(
            '#display .pane_content {\n  background: #191919;\n}',
            '#display .pane_content {\n  background: #f8f9fa;\n  border: 1px solid #dee2e6;\n  color: #222;\n}'
        ).replace(
            '#display th {\n  background: #212121\n}',
            '#display th {\n  background: #f8f9fa\n}'
        ).replace(
            'td {\n  border-bottom: 1px solid #111;\n}',
            'td {\n  border-bottom: 1px solid #dee2e6;\n}'
        )

        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error reading HTML for lens {lens_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

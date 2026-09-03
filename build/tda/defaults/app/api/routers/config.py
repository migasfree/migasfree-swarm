"""
Configuration and Metadata Catalogs API Endpoints
"""
import os
import json
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from core.config import (
    TDA_DIR,
    TDA_CONFIG_PATH,
    FORMULA_PREFIX_DEFAULT,
    LENS_COLORS_DEFAULT,
    DEFAULT_LENS_COLOR,
    AVAILABLE_COLOR_COLUMNS,
    AVAILABLE_METRIC_COLUMNS,
    logger,
)
from core.auth import get_core_staff_user
from api.models import TdaConfig
from lens_store import load_all_lenses, DATASET_METRICS

router = APIRouter(prefix="/api/v1/config", tags=["config"])

AVAILABLE_DATASET_METRICS = [
    m for m in AVAILABLE_METRIC_COLUMNS if m["name"] in set(DATASET_METRICS)
]


@router.get("")
async def get_config(user: dict = Depends(get_core_staff_user)):
    """
    Return the current TDA configuration from disk.
    If the config file does not exist, returns the default values.
    """
    try:
        if os.path.isfile(TDA_CONFIG_PATH):
            with open(TDA_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {"formula_prefix_ids": FORMULA_PREFIX_DEFAULT, "metrics_interval_days": 365}
        if "metrics_interval_days" not in cfg:
            cfg["metrics_interval_days"] = 365
        raw_colors = cfg.get("lens_colors", {})
        if not isinstance(raw_colors, dict):
            raw_colors = {}
        merged_colors = {**LENS_COLORS_DEFAULT, **raw_colors}
        for spec in load_all_lenses():
            merged_colors.setdefault(spec["name"], dict(DEFAULT_LENS_COLOR))
        cfg["lens_colors"] = merged_colors
        return JSONResponse(content=cfg)
    except Exception as e:
        logger.error(f"Error reading TDA config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def save_config(config: TdaConfig, user: dict = Depends(get_core_staff_user)):
    """
    Save TDA configuration to disk.
    Requires Staff or Superuser authentication.
    The config is immediately effective for the next TDA run (no restart needed).
    """
    try:
        os.makedirs(TDA_DIR, exist_ok=True)
        payload = config.model_dump()
        if not payload.get("lens_colors"):
            existing_colors = {}
            if os.path.isfile(TDA_CONFIG_PATH):
                try:
                    with open(TDA_CONFIG_PATH, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                    existing_colors = existing.get("lens_colors", {})
                except Exception:
                    pass
            payload["lens_colors"] = existing_colors
        with open(TDA_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        logger.info(f"TDA config saved by {user.get('username', '?')}: {payload}")
        return JSONResponse(content={"status": "saved", "config": payload})
    except Exception as e:
        logger.error(f"Error saving TDA config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-color-columns")
async def get_available_color_columns(user: dict = Depends(get_core_staff_user)):
    """
    Return the numeric columns usable to color the Mapper graph nodes, plus
    the core_property prefixes (as prefix_<id>).
    """
    options = [dict(o, group="metric") for o in AVAILABLE_COLOR_COLUMNS]
    try:
        from database import query_dataframe

        df_prefixes = query_dataframe(
            "SELECT id, prefix, name FROM core_property WHERE enabled = TRUE ORDER BY name"
        )
        if df_prefixes is not None and not df_prefixes.empty:
            for _, row in df_prefixes.iterrows():
                try:
                    pid = int(row["id"])
                except (ValueError, TypeError):
                    continue
                options.append({
                    "columns": [f"prefix_{pid}"],
                    "label": str(row["name"]),
                    "kind": "categorical",
                    "group": "attribute",
                })
        options.sort(key=lambda o: o.get("group") != "attribute")
    except Exception as exc:
        logger.warning(f"Could not load prefix color columns: {exc}")
    return JSONResponse(content=options)


@router.get("/available-metric-columns")
async def get_available_metric_columns(user: dict = Depends(get_core_staff_user)):
    """Return the numeric columns usable as projection metrics in user-defined lenses."""
    return JSONResponse(content=AVAILABLE_METRIC_COLUMNS)


@router.get("/available-dataset-metrics")
async def get_available_dataset_metrics(user: dict = Depends(get_core_staff_user)):
    """Return the numeric metric columns selectable in the DATASET section."""
    return JSONResponse(content=AVAILABLE_DATASET_METRICS)


@router.get("/available-prefixes")
async def get_available_prefixes(user: dict = Depends(get_core_staff_user)):
    """Return all formula property types available in the database."""
    from database import query_dataframe
    try:
        df = query_dataframe(
            "SELECT id, prefix, name FROM core_property "
            "WHERE enabled = TRUE ORDER BY name"
        )
        if df.empty:
            return JSONResponse(content=[])
        result = [
            {"id": int(row["id"]), "prefix": row["prefix"], "name": row["name"]}
            for _, row in df.iterrows()
        ]
        return JSONResponse(content=result)
    except Exception as e:
        logger.warning(f"Could not fetch available prefixes (DB may be unavailable): {e}")
        return JSONResponse(content=[])


@router.get("/available-scopes")
async def get_available_scopes(user: dict = Depends(get_core_staff_user)):
    """Return the scopes owned by the authenticated user."""
    import scopes
    try:
        result = scopes.available_scopes(user.get("username"))
        return JSONResponse(content=result)
    except Exception as e:
        logger.warning(f"Could not fetch available scopes (DB may be unavailable): {e}")
        return JSONResponse(content=[])


@router.get("/estimate-matrix")
async def estimate_matrix(
    user: dict = Depends(get_core_staff_user),
    formula_prefix_ids: List[int] = Query(default=[]),
    scope_ids: List[int] = Query(default=[]),
    metric_columns: List[str] = Query(default=[]),
):
    """Estimate the size of the N×D feature matrix for a given DATASET selection."""
    from tda_engine import estimate_matrix_counts
    try:
        counts = estimate_matrix_counts(
            formula_prefix_ids, scope_ids, metric_columns
        )
    except Exception as exc:
        logger.warning(f"Could not estimate matrix size (DB may be unavailable): {exc}")
        raise HTTPException(status_code=503, detail="Database unavailable")

    return JSONResponse(content=counts)

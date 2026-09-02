"""
TDA Standalone Web Application & API (FastAPI)
Serves the Cytoscape Dashboard, REST endpoints, KeplerMapper diagnostic HTML,
and handles on-demand background recalculation triggers.
Protected by Migasfree Core (Django) Staff Authentication.
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
import httpx
from pydantic import BaseModel, field_validator
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Depends, status, Response, Cookie, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import tda_worker

from lens_store import (
    load_all_lenses,
    load_lens,
    save_lens,
    delete_lens,
    validate_lens,
    seed_builtin_lenses,
    migrate_legacy_outputs,
    has_lens_output,
    legacy_output_path,
    lens_output_path,
    LENS_TYPE_LABELS,
    DATASET_METRICS,
)

import time

logger = logging.getLogger("migasfree-tda")
logging.getLogger("httpx").setLevel(logging.WARNING)

TDA_DIR = "/data/tda"
TDA_CONFIG_PATH = os.path.join(TDA_DIR, "config.json")
APP_DIR = os.path.dirname(os.path.abspath(__file__))

CORE_URL = os.getenv("CORE_URL", "http://core:8080")
CORE_LOGIN_URL = f"{CORE_URL}/rest-auth/login/"
CORE_USER_URL = f"{CORE_URL}/rest-auth/user/"

# Short in-memory token cache (TTL: 10 seconds) to avoid spamming Core during polling
_AUTH_CACHE: dict[str, tuple[dict, float]] = {}
AUTH_CACHE_TTL = 10.0


class EndpointFilter(logging.Filter):
    def __init__(self, excluded_endpoints: tuple = ("/health", "/api/v1/health", "/api/v1/status")):
        super().__init__()
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        # Check formatted message
        try:
            msg = record.getMessage()
            if any(endpoint in msg for endpoint in self.excluded_endpoints):
                return False
        except Exception:
            pass
        # Check raw args
        if record.args:
            for arg in record.args:
                if isinstance(arg, str) and any(endpoint in arg for endpoint in self.excluded_endpoints):
                    return False
        return True


# Attach filter to uvicorn loggers
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
logging.getLogger("uvicorn").addFilter(EndpointFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure filter is active on uvicorn access logger
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # Start scheduler thread on startup
    logger.info("Initializing TDA Web Service and starting background scheduler...")
    seed_builtin_lenses()
    migrate_legacy_outputs()
    tda_worker.start_scheduler_thread()
    yield
    logger.info("Shutting down TDA Web Service...")


app = FastAPI(
    title="Migasfree TDA Service",
    description="Topological Data Analysis microservice for Migasfree (Staff protected)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Mount static files
static_dir = os.path.join(APP_DIR, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates_dir = os.path.join(APP_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)


class LoginRequest(BaseModel):
    username: str
    password: str


FORMULA_PREFIX_DEFAULT = [3, 5]

LENS_COLORS_DEFAULT = {
    "health": {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"},
    "obsolescence": {"columns": ["ram_gb"], "label": "RAM (GB)", "kind": "continuous"},
    "sync": {"columns": ["avg_sync_duration_secs"], "label": "Avg Sync Duration (secs)", "kind": "continuous"},
    "software": {"columns": ["total_packages"], "label": "Total Installed Packages", "kind": "continuous"},
    "migration": {"columns": ["migration_count"], "label": "Migrations Count", "kind": "continuous"},
    "diversity": {"columns": ["jaccard_outlier_score"], "label": "Configuration Outlier Score (Mean Jaccard Distance)", "kind": "continuous"},
}

DEFAULT_LENS_COLOR = {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"}

COLOR_KINDS = ("continuous", "categorical")

AVAILABLE_COLOR_COLUMNS = [
    {"columns": ["error_count"], "label": "Error Count", "kind": "continuous"},
    {"columns": ["fault_count"], "label": "Fault Count", "kind": "continuous"},
    {"columns": ["sync_count"], "label": "Sync Count", "kind": "continuous"},
    {"columns": ["avg_sync_duration_secs"], "label": "Avg Sync Duration (secs)", "kind": "continuous"},
    {"columns": ["pms_failures"], "label": "PMS Failures", "kind": "continuous"},
    {"columns": ["ram_gb"], "label": "RAM (GB)", "kind": "continuous"},
    {"columns": ["disk_gb"], "label": "Disk (GB)", "kind": "continuous"},
    {"columns": ["machine_type"], "label": "Machine Type (Virtual/Physical)", "kind": "continuous"},
    {"columns": ["computer_age_days"], "label": "Computer Age (days)", "kind": "continuous"},
    {"columns": ["days_since_last_sync"], "label": "Days Since Last Sync", "kind": "continuous"},
    {"columns": ["total_packages"], "label": "Total Installed Packages", "kind": "continuous"},
    {"columns": ["migration_count"], "label": "Migrations Count", "kind": "continuous"},
    {"columns": ["days_since_last_migration"], "label": "Days Since Last Migration", "kind": "continuous"},
    {"columns": ["jaccard_outlier_score"], "label": "Configuration Outlier Score (diversity)", "kind": "continuous"},
    {"columns": ["software_drift_score"], "label": "Software Drift Score (software)", "kind": "continuous"},
]

# Numeric columns usable as projection metrics in user-defined lenses.
# Every entry is a single df_computers column with its human-readable label.
AVAILABLE_METRIC_COLUMNS = [
    {"name": "error_count", "label": "Error Count"},
    {"name": "fault_count", "label": "Fault Count"},
    {"name": "sync_count", "label": "Sync Count"},
    {"name": "avg_sync_duration_secs", "label": "Avg Sync Duration (secs)"},
    {"name": "pms_failures", "label": "PMS Failures"},
    {"name": "ram_gb", "label": "RAM (GB)"},
    {"name": "disk_gb", "label": "Disk (GB)"},
    {"name": "machine_type", "label": "Machine Type (Virtual/Physical)"},
    {"name": "computer_age_days", "label": "Computer Age (days)"},
    {"name": "days_since_last_sync", "label": "Days Since Last Sync"},
    {"name": "total_packages", "label": "Total Installed Packages"},
    {"name": "migration_count", "label": "Migrations Count"},
    {"name": "days_since_last_migration", "label": "Days Since Last Migration"},
    {"name": "jaccard_outlier_score", "label": "Configuration Outlier Score (diversity)"},
    {"name": "software_drift_score", "label": "Software Drift Score (software)"},
]

# Numeric metric columns selectable in the DATASET section (raw metrics only,
# excluding the drift scores computed during projection).
AVAILABLE_DATASET_METRICS = [
    m for m in AVAILABLE_METRIC_COLUMNS if m["name"] in set(DATASET_METRICS)
]


class TdaConfig(BaseModel):
    formula_prefix_ids: List[int]
    lens_colors: dict = {}
    metrics_interval_days: Optional[int] = 365

    @field_validator("formula_prefix_ids")
    @classmethod
    def validate_ids(cls, v):
        cleaned = [i for i in v if i > 0]
        if not cleaned:
            raise ValueError("formula_prefix_ids must contain at least one positive integer")
        return cleaned

    @field_validator("lens_colors")
    @classmethod
    def validate_lens_colors(cls, v):
        if not isinstance(v, dict):
            raise ValueError("lens_colors must be an object")
        cleaned = {}
        for lens, entry in v.items():
            if not isinstance(entry, dict):
                continue
            fallback = LENS_COLORS_DEFAULT.get(lens, DEFAULT_LENS_COLOR)
            columns = entry.get("columns")
            if not columns:
                columns = fallback["columns"]
            elif isinstance(columns, (list, tuple)):
                columns = [str(c) for c in columns if str(c).strip()]
            else:
                columns = [str(columns)]
            if not columns:
                columns = fallback["columns"]
            entry_kind = entry.get("kind")
            if entry_kind is not None and str(entry_kind) in COLOR_KINDS:
                kind = str(entry_kind)
            elif "project_encoded" in columns:
                kind = "categorical"
            else:
                kind = str(fallback.get("kind") or "continuous")
            cleaned[lens] = {
                "columns": list(columns),
                "label": str(entry.get("label") or fallback["label"]),
                "kind": kind,
            }
        return cleaned


class LensColor(BaseModel):
    columns: List[str] = []
    label: str = ""
    kind: str = "continuous"


class LensDataset(BaseModel):
    formula_prefix_ids: List[int] = []
    scope_ids: List[int] = []
    metric_columns: List[str] | None = None


class LensSection(BaseModel):
    type: str = "pca"
    components: int = 2
    metric_columns: List[str] = []
    matrix_source: str | None = None


class CoverSection(BaseModel):
    type: str = "cubical"
    n_cubes: int | None = None
    overlap: float | None = None
    radius: float | None = None
    n_neighbors: int | None = None


class ClusteringSection(BaseModel):
    scaling: bool = True
    type: str = "dbscan"
    n_clusters: int | None = None
    eps: float | None = None
    min_samples: int | None = None


class DrawSection(BaseModel):
    dimensions: int = 3
    iterations: int | None = None
    seed: int | None = None
    color: LensColor | None = None
    node_label: str = "attribute"


class LensSpec(BaseModel):
    name: str
    label: str
    description: str = ""
    lens: LensSection | None = None
    cover: CoverSection | None = None
    clustering: ClusteringSection | None = None
    draw: DrawSection | None = None
    dataset: LensDataset | None = None
    builtin: bool = False

    def to_descriptor(self, current_name=None) -> dict:
        """Validate and normalize into a lens_store descriptor."""
        raw = {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "lens": self.lens.model_dump() if self.lens else None,
            "cover": self.cover.model_dump() if self.cover else None,
            "clustering": self.clustering.model_dump() if self.clustering else None,
            "draw": self.draw.model_dump() if self.draw else None,
            "dataset": self.dataset.model_dump() if self.dataset else None,
            "builtin": self.builtin,
        }
        return validate_lens(raw, current_name=current_name)


async def get_core_staff_user(request: Request) -> dict:
    """
    Authenticate user against Migasfree Core (Django) and ensure is_staff or is_superuser.
    Extracts token from:
      1. Cookie 'mf_token' or 'tda_token' or 'auth_token'
      2. Header 'Authorization: Bearer <token>' or 'Authorization: Token <token>'
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() in ("bearer", "token"):
            token = parts[1]

    if not token:
        token = request.cookies.get("mf_token") or request.cookies.get("tda_token") or request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = time.time()
    if token in _AUTH_CACHE:
        cached_user, timestamp = _AUTH_CACHE[token]
        if now - timestamp < AUTH_CACHE_TTL:
            return cached_user

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                CORE_USER_URL,
                headers={"Authorization": f"Token {token}"}
            )

        if resp.status_code != 200:
            _AUTH_CACHE.pop(token, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = resp.json()
        is_staff = user_data.get("is_staff", False)
        is_superuser = user_data.get("is_superuser", False)

        if not (is_staff or is_superuser):
            _AUTH_CACHE.pop(token, None)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff privileges required to access TDA service",
            )

        _AUTH_CACHE[token] = (user_data, now)
        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating token with Migasfree Core: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to verify authentication with Core: {e}",
        )


# ─── Auth Endpoints ─────────────────────────────────────────────────────────

@app.post("/api/v1/auth/login")
async def login(login_req: LoginRequest, response: Response):
    """
    Authenticate against Django rest-auth and set secure cookie.
    Only allows users with is_staff or is_superuser.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            auth_resp = await client.post(
                CORE_LOGIN_URL,
                json={"username": login_req.username, "password": login_req.password},
            )

        if auth_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token_data = auth_resp.json()
        token = token_data.get("key") or token_data.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token not returned by Core",
            )

        # Validate staff permissions
        async with httpx.AsyncClient(timeout=10.0) as client:
            user_resp = await client.get(
                CORE_USER_URL,
                headers={"Authorization": f"Token {token}"}
            )

        if user_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to fetch user profile")

        user_data = user_resp.json()
        if not (user_data.get("is_staff") or user_data.get("is_superuser")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff or superuser privileges required to access TDA Dashboard",
            )

        # Set cookie directly on the returned JSONResponse
        res = JSONResponse(content={
            "status": "success",
            "token": token,
            "user": {
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "is_staff": user_data.get("is_staff"),
                "is_superuser": user_data.get("is_superuser"),
            }
        })
        res.set_cookie(
            key="tda_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/",
            max_age=86400 * 7,
        )
        return res

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/auth/logout")
async def logout():
    """Clear the session cookie."""
    res = JSONResponse(content={"status": "logged_out"})
    res.delete_cookie(key="tda_token", path="/")
    res.delete_cookie(key="mf_token", path="/")
    res.delete_cookie(key="auth_token", path="/")
    return res


@app.get("/api/v1/auth/me")
async def current_user(user: dict = Depends(get_core_staff_user)):
    """Return currently authenticated staff user info."""
    return JSONResponse(content={
        "username": user.get("username"),
        "email": user.get("email"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "is_staff": user.get("is_staff"),
        "is_superuser": user.get("is_superuser"),
    })


# ─── Healthcheck Endpoint (Unauthenticated for Docker/Swarm) ───────────────

@app.get("/health")
@app.get("/api/v1/health")
async def health():
    """Liveness probe for Docker container healthcheck."""
    return JSONResponse(content={"status": "healthy"})


# ─── Dashboard & Visualizations ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def tda_dashboard(request: Request):
    """Render the main interactive TDA Dashboard."""
    lenses_env = os.getenv("TDA_LENSES", "health,obsolescence,software,migration,sync,diversity")
    configured_lenses = [l.strip() for l in lenses_env.split(",") if l.strip()]
    return templates.TemplateResponse(
        request,
        "tda.html",
        {"configured_lenses": configured_lenses}
    )


@app.get("/api/v1/status")
async def get_status(user: dict = Depends(get_core_staff_user)):
    """Return the current processing status of the TDA engine."""
    return JSONResponse(content=tda_worker.get_status())


@app.post("/api/v1/recalculate")
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


@app.get("/api/v1/lenses")
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


@app.get("/api/v1/lenses/details")
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


@app.get("/api/v1/lenses/{lens_name}")
async def get_lens(lens_name: str, user: dict = Depends(get_core_staff_user)):
    """Return a single lens descriptor."""
    spec = load_lens(lens_name)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Lens '{lens_name}' not found")
    lens_type = (spec.get("lens") or {}).get("type", "pca")
    spec["projection_label"] = LENS_TYPE_LABELS.get(lens_type, lens_type)
    return JSONResponse(content=spec)


@app.post("/api/v1/lenses")
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


@app.put("/api/v1/lenses/{lens_name}")
async def update_lens(lens_name: str, spec: LensSpec, user: dict = Depends(get_core_staff_user)):
    """Update a lens descriptor (name immutable for built-in lenses)."""
    existing = load_lens(lens_name)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Lens '{lens_name}' not found")
    if existing.get("builtin") and not spec.builtin:
        # Preserve the built-in flag regardless of the client payload
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


@app.delete("/api/v1/lenses/{lens_name}")
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


@app.post("/api/v1/lenses/{lens_name}/recalculate")
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


@app.get("/api/v1/lens/{lens_name}/json")
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


@app.get("/api/v1/lens/{lens_name}/html")
async def get_lens_html(lens_name: str, user: dict = Depends(get_core_staff_user)):
    """Return the KeplerMapper diagnostic HTML visualization."""
    html_path = _resolve_lens_file(lens_name, "html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail=f"Lens HTML for '{lens_name}' not found")

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Clean KeplerMapper styling for light theme
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


# ─── Settings Page & Config API ──────────────────────────────────────────────

@app.get("/settings", response_class=HTMLResponse)
async def tda_settings(request: Request):
    """Render the TDA settings/configuration page."""
    lenses_env = os.getenv("TDA_LENSES", "health,obsolescence,software,migration,sync,diversity")
    configured_lenses = [l.strip() for l in lenses_env.split(",") if l.strip()]
    return templates.TemplateResponse(
        request,
        "tda_settings.html",
        {"configured_lenses": configured_lenses}
    )


@app.get("/api/v1/config")
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
        # Merge per-lens coloring with defaults so every configured lens
        # always has an explicit entry (customized or not)
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


@app.post("/api/v1/config")
async def save_config(config: TdaConfig, user: dict = Depends(get_core_staff_user)):
    """
    Save TDA configuration to disk.
    Requires Staff or Superuser authentication.
    The config is immediately effective for the next TDA run (no restart needed).
    """
    try:
        os.makedirs(TDA_DIR, exist_ok=True)
        payload = config.model_dump()
        # Preserve existing per-lens colors when the payload does not set them
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


@app.get("/api/v1/config/available-color-columns")
async def get_available_color_columns(user: dict = Depends(get_core_staff_user)):
    """
    Return the numeric columns usable to color the Mapper graph nodes, plus
    the core_property prefixes (as prefix_<id>). Selecting a prefix colors each
    node by its dominant concrete value (e.g. CTX-aula). The Settings UI filters
    this catalog by the Attribute types and Metrics selected in each lens DATASET.
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


@app.get("/api/v1/config/available-metric-columns")
async def get_available_metric_columns(user: dict = Depends(get_core_staff_user)):
    """
    Return the numeric columns usable as projection metrics in user-defined lenses.
    Used to populate the lens designer metric selects in Settings.
    """
    return JSONResponse(content=AVAILABLE_METRIC_COLUMNS)


@app.get("/api/v1/config/available-dataset-metrics")
async def get_available_dataset_metrics(user: dict = Depends(get_core_staff_user)):
    """
    Return the numeric metric columns selectable in the DATASET section.
    Used to populate the dataset metric multi-select in Settings.
    """
    return JSONResponse(content=AVAILABLE_DATASET_METRICS)


@app.get("/api/v1/config/available-prefixes")
async def get_available_prefixes(user: dict = Depends(get_core_staff_user)):
    """
    Return all formula property types available in the database.
    Used to populate the prefix multi-select in Settings.
    Returns [] if the database is unavailable.
    """
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


@app.get("/api/v1/config/available-scopes")
async def get_available_scopes(user: dict = Depends(get_core_staff_user)):
    """
    Return the scopes owned by the authenticated user.
    Used to populate the scope multi-select in Settings.
    Returns [] if the database is unavailable.
    """
    import scopes
    try:
        result = scopes.available_scopes(user.get("username"))
        return JSONResponse(content=result)
    except Exception as e:
        logger.warning(f"Could not fetch available scopes (DB may be unavailable): {e}")
        return JSONResponse(content=[])


@app.get("/api/v1/config/estimate-matrix")
async def estimate_matrix(
    user: dict = Depends(get_core_staff_user),
    formula_prefix_ids: List[int] = Query(default=[]),
    scope_ids: List[int] = Query(default=[]),
    metric_columns: List[str] = Query(default=[]),
):
    """
    Estimate the size of the N×D feature matrix for a given DATASET selection.

    Returns:
        n               - number of computers (rows) matching the filters
        d_attr          - number of binary attribute columns
        n_metric        - number of selected metric columns
        d_max           - upper bound on D (= d_attr + n_metric); the final D
                          can be smaller after zero-variance columns are dropped
        estimated_bytes - dense float32 matrix footprint (n * d_max * 4)
    """
    from tda_engine import estimate_matrix_counts
    try:
        counts = estimate_matrix_counts(
            formula_prefix_ids, scope_ids, metric_columns
        )
    except Exception as exc:
        logger.warning(f"Could not estimate matrix size (DB may be unavailable): {exc}")
        raise HTTPException(status_code=503, detail="Database unavailable")

    return JSONResponse(content=counts)

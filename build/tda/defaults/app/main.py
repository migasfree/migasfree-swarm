"""
TDA Standalone Web Application & API (FastAPI)
Serves the Cytoscape/3D Dashboard, REST endpoints, KeplerMapper diagnostic HTML,
and handles on-demand background recalculation triggers.
Protected by Migasfree Core (Django) Staff Authentication.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.config import APP_DIR, logger
import tda_worker
from lens_store import seed_builtin_lenses, migrate_legacy_outputs

from api.routers.system import router as system_router
from api.routers.auth import router as auth_router
from api.routers.views import router as views_router
from api.routers.lenses import router as lenses_router
from api.routers.config import router as config_router


class EndpointFilter(logging.Filter):
    def __init__(self, excluded_endpoints: tuple = ("/health", "/api/v1/health", "/api/v1/status")):
        super().__init__()
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            if any(endpoint in msg for endpoint in self.excluded_endpoints):
                return False
        except Exception:
            pass
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
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
    logging.getLogger("httpx").setLevel(logging.WARNING)
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

# Include Modular Routers
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(views_router)
app.include_router(lenses_router)
app.include_router(config_router)

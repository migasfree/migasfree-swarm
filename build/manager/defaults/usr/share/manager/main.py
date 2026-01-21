import logging

from jinja2 import Template
from datetime import datetime

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import ROOT_PATH
from routers import (
    admin,
    computer,
    crl,
    ca,
    auth,
    status,
    extensions,
    tunnel,
    availability,
    metrics,
)
from routers.status import lifespan


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Migasfree Manager API",
    version="1.0.0",
    description="API for Migasfree Manager",
    root_path=ROOT_PATH,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="manager-static")

app.include_router(auth.router_private)
app.include_router(admin.router_public)
app.include_router(admin.router_private)
app.include_router(computer.router_public)
app.include_router(computer.router_private)
app.include_router(crl.router_public)
app.include_router(ca.router_public)
app.include_router(status.router)
app.include_router(status.router_internal)
app.include_router(status.router_private)
app.include_router(status.router_public)
app.include_router(extensions.router_private)
app.include_router(tunnel.router)
app.include_router(availability.router)
app.include_router(metrics.router_private)


@app.get("/v1/internal/health", tags=["status"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/img/mtls.svg")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Migasfree Manager API",
        "docs": f"{ROOT_PATH}/docs",
        "health": f"{ROOT_PATH}/v1/internal/health",
    }


@app.get("/manifest")
async def manifest():
    """Cache manifest"""
    template = """CACHE MANIFEST
/manager/v1/private/status
/manager/static/*
    """
    content = Template(template).render({})

    return Response(content=content, media_type="text/cache-manifest")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

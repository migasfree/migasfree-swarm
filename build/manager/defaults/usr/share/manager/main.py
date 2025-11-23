import logging

from fastapi import FastAPI
from datetime import datetime
from routers import admin, computer, crl, auth

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.config import ROOT_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Certificate Authority API",
    version="1.0.0",
    description="API for certificate management with local CA",
    root_path=ROOT_PATH
)

app.mount("/static", StaticFiles(directory="static"), name="ca-static")

app.include_router(auth.router_private)
app.include_router(admin.router_public)
app.include_router(admin.router_private)
app.include_router(computer.router_public)
app.include_router(computer.router_private)
app.include_router(crl.router_public)


@app.get('/health', tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/img/mtls.svg")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Certificate Authority API",
        "docs": f"{ROOT_PATH}/docs",
        "health": f"{ROOT_PATH}/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from core.config import API_VERSION, STACK, PATH_CERTIFICATES

router_public = APIRouter(
    prefix=f"{API_VERSION}/public",
    tags=["ca"]
)
logger = logging.getLogger(__name__)


@router_public.get("/ca")
async def get_ca():
    """Gets the Certificate Authority (CA)"""

    file_ca = PATH_CERTIFICATES / STACK / "ca/ca.crt"
    if not file_ca.exists():
        logger.warning(f"CA not found for stack {STACK}")
        raise HTTPException(status_code=404, detail="CA not found")

    try:
        ca_data = file_ca.read_bytes()

        return Response(
            content=ca_data,
            media_type='application/pkix-cert',
            headers={
                'Content-Disposition': 'attachment; filename="ca.pem"',
                'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Content-Length': str(len(ca_data))
            }
        )
    except Exception as e:
        logger.error(f"Error serving CA: {e}")
        raise HTTPException(status_code=500, detail='Error serving CA')

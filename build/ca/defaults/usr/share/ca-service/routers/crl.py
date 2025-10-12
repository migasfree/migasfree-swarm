from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from core.config import ROOT, PATH_CERTIFICATES

from core.security import (
    get_stack_dependency
)


router = APIRouter(
    prefix=f"{ROOT}/{{stack}}",
    tags=["crl"]
)


@router.get("/crl")
async def get_crl(stack: str = Depends(get_stack_dependency)):
    """Obtiene la Lista de Revocación de Certificados (CRL) para usuarios del stack"""

    file_crl = PATH_CERTIFICATES / stack / "crl.pem"
    if not file_crl.exists():
        logger.warning(f"CRL not found for stack {stack}")
        raise HTTPException(status_code=404, detail="CRL not found")

    try:
        crl_data = file_crl.read_bytes()

        return Response(
            content=crl_data,
            media_type='application/pkix-crl',
            headers={
                'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
                'Pragma': 'no-cache',
                'Connection': 'close',
                'Content-Length': str(len(crl_data))
            }
        )
    except Exception as e:
        logger.error(f"Error serving CRL: {e}")
        raise HTTPException(status_code=500, detail='Error serving CRL')

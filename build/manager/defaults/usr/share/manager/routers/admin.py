import logging
import time
import secrets

from fastapi import APIRouter, Request, HTTPException, Form, Body, status, Depends
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from datetime import datetime, timedelta
from typing import Optional

from core.config import ROOT_PATH, API_VERSION, STACK, PATH_CERTIFICATES
from core.security import (
    TokenValidator,
    create_admin_cert,
    revoke_admin_cert
)
from core.models import TokenAdminResponse, TokenCreateRequest
from core.utils import get_fqdn, get_host
from core.core_client import get_current_superuser

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

router_public = APIRouter(
    prefix=f"{API_VERSION}/public/mtls",
    tags=["mtls-admin"]
)

router_private = APIRouter(
    prefix=f"{API_VERSION}/private/mtls",
    tags=["mtls-admin"]
)


@router_private.post(
    '/admin-tokens',
    response_model=TokenAdminResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_token(
    data: TokenCreateRequest,
    currentuser: dict = Depends(get_current_superuser)
):
    """
    Create a token for the issuance of an mTLS certificate for an administrator.
    """
    token = secrets.token_hex(32)
    # expires_at = datetime.utcnow() + timedelta(hours=72)

    stack_token_dir = PATH_CERTIFICATES / STACK / "admin" / "tokens"
    stack_token_dir.mkdir(parents=True, exist_ok=True)

    # Save common_name|validity_days
    token_file = stack_token_dir / token
    content = f"{data.common_name}|{data.validity_days}"
    token_file.write_text(content, encoding='utf-8')

    logger.info(f"Token created for CN={data.common_name} in stack={STACK}")
    host = get_host(STACK)
    return TokenAdminResponse(url=f"https://{host}{ROOT_PATH}/v1/public/mtls/admin-requests/{token}")


@router_public.get("/admin-requests/{token}", response_class=HTMLResponse)
async def admin_request_form(
    request: Request,
    token: str
):
    """
    mTLS Certificate Issuance Form for administrators.
    """
    token_file_path = PATH_CERTIFICATES / STACK / "admin" / "tokens" / token
    if not token_file_path.exists():
        raise HTTPException(status_code=404, detail="Token not found")

    creation_time = datetime.fromtimestamp(token_file_path.stat().st_ctime)
    if datetime.utcnow() - creation_time > timedelta(hours=72):
        token_file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Token expired")

    content = token_file_path.read_text(encoding='utf-8')
    try:
        common_name, validity_days = content.split('|')
    except Exception:
        raise HTTPException(status_code=500, detail="Corrupted token file content")

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "common_name": common_name,
            "validity_days": int(validity_days),
            "token": token,
            "fqdn": get_fqdn(STACK),
            "stack": STACK,
            "root_path": ROOT_PATH
        }
    )


@router_public.post("/admin-certificates")
async def create_admin_certificate(
    token: str = Form(...),
    email: EmailStr = Form(...),
    password: Optional[str] = Form(None)
):
    """
    mTLS Certificate Issuance for administrators.
    """

    validator = TokenValidator(STACK, token, "admin")
    common_name, validity_days = validator.validate()
    FQDN = get_fqdn(STACK)
    HOST = get_host(STACK)

    success = create_admin_cert(
        FQDN, HOST, STACK, common_name, password, validity_days, email
    )

    if not success:
        logger.error(f"Failed to create certificate for {email}")
        raise HTTPException(status_code=500, detail="Certificate creation failed")

    cert_name = f"{common_name}"
    cert_dir = PATH_CERTIFICATES / STACK / "admin" / "certs"
    file_tar = cert_dir / f"{cert_name}.tar"

    if not file_tar.exists():
        logger.error(f"Certificate file not found: {file_tar}")
        time.sleep(3)
        raise HTTPException(status_code=500, detail="Certificate file not found")

    try:
        content = file_tar.read_bytes()
        validator.consume()
        file_tar.unlink()

        logger.info(f"Certificate delivered for {email} in stack {STACK}")

        return Response(
            content=content,
            media_type='application/x-tar',
            headers={
                'Content-Disposition': f'attachment; filename="{cert_name}_{FQDN}.tar"',
                'Content-Length': str(len(content)),
                'Cache-Control': 'no-store, no-cache, must-revalidate',
                'Pragma': 'no-cache'
            }
        )
    except Exception as e:
        logger.error(f"Error serving certificate: {e}")
        raise HTTPException(status_code=500, detail="Error serving certificate")


@router_private.delete("/admin-certificates", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_admin_certificate(
    common_name: str = Body(..., embed=True),
    currentuser: dict = Depends(get_current_superuser)
):
    """
    mTLS Certificate Revocation for administrators.
    """

    try:
        revoked = revoke_admin_cert(common_name, STACK)
        if not revoked:
            logger.warning(f"Attempt to revoke non-existent or already revoked cert: {common_name} in stack {STACK}")
            raise HTTPException(status_code=404, detail="Certificate not found or already revoked")

        logger.info(f"Certificate revoked for {common_name} in stack {STACK}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Error revoking certificate for {common_name} in stack {STACK}: {e}")
        raise HTTPException(status_code=500, detail="Error revoking certificate")

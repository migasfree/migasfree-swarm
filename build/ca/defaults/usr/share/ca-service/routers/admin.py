from fastapi import APIRouter, Request, HTTPException, Form, Depends, Query, Body, status
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from datetime import datetime, timedelta
from typing import Optional
import logging
import time
import secrets

from core.config import ROOT, PATH_CERTIFICATES

from core.security import (
    get_stack_dependency,
    TokenValidator,
    create_admin_cert,
    revoke_admin_cert
)

from core.models import TokenCreateResponse, TokenCreateRequest

from core.utils import get_fqdn, get_host


logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix=f"{ROOT}/{{stack}}/admin",
    tags=["admin-certificates"]
)


@router.post(
    '/token',
    response_model=TokenCreateResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_token(
    data: TokenCreateRequest,
    stack: str = Depends(get_stack_dependency)
):
    """Create a temporary token for certificate request in a specific stack"""


    token = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(hours=72)

    stack_token_dir = PATH_CERTIFICATES / stack / "admin" / "tokens"
    stack_token_dir.mkdir(parents=True, exist_ok=True)

    # Save common_name|validity_days
    token_file = stack_token_dir / token
    content = f"{data.common_name}|{data.validity_days}"
    token_file.write_text(content, encoding='utf-8')

    logger.info(f"Token created for CN={data.common_name} in stack={stack}")
    host = get_host(stack)
    return TokenCreateResponse(url=f"https://{host}/ca/v1/{stack}/admin/token/{token}")

@router.get("/token/{token}", response_class=HTMLResponse)
async def get_admin_cert_request_form(
    request: Request,
    token: str ,
    stack: str = Depends(get_stack_dependency)
):
    token_file_path =  PATH_CERTIFICATES / stack / "admin" / "tokens" / token
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
            "fqdn": get_fqdn(stack),
            "stack": stack
        }
    )


@router.post("")
async def create_admin_certificate(
    token: str = Form(...),
    email: EmailStr = Form(...),
    password: Optional[str] = Form(None),
    stack: str = Depends(get_stack_dependency)
):
    """Creates a user certificate in a specific stack"""

    validator = TokenValidator(stack, token, "admin")
    common_name, validity_days = validator.validate()
    FQDN = get_fqdn(stack)
    HOST = get_host(stack)

    success = create_admin_cert(
        FQDN, HOST, stack, common_name, password, validity_days, email
    )

    if not success:
        logger.error(f"Failed to create certificate for {email}")
        raise HTTPException(status_code=500, detail="Certificate creation failed")

    cert_name = f"{common_name}"
    cert_dir = PATH_CERTIFICATES / stack / "admin" / "certs"
    file_tar = cert_dir / f"{cert_name}.tar"

    if not file_tar.exists():
        logger.error(f"Certificate file not found: {file_tar}")
        time.sleep(3)
        raise HTTPException(status_code=500, detail="Certificate file not found")

    try:
        content = file_tar.read_bytes()
        validator.consume()
        file_tar.unlink()

        logger.info(f"Certificate delivered for {email} in stack {stack}")

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


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_admin_certificate(
    common_name: str = Body(..., embed=True),
    stack: str = Depends(get_stack_dependency)
):
    """
    Revokes the admin certificate identified by common_name in a specific stack.
    """

    try:
        revoked = revoke_admin_cert(common_name, stack)
        if not revoked:
            logger.warning(f"Attempt to revoke non-existent or already revoked cert: {common_name} in stack {stack}")
            raise HTTPException(status_code=404, detail="Certificate not found or already revoked")

        logger.info(f"Certificate revoked for {common_name} in stack {stack}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Error revoking certificate for {common_name} in stack {stack}: {e}")
        raise HTTPException(status_code=500, detail="Error revoking certificate")
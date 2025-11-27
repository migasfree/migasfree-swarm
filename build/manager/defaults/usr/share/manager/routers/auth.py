from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestFormStrict
from pydantic import BaseModel
import httpx
from core.config import API_VERSION, CORE_LOGIN_URL

router_private = APIRouter(
    prefix=f"{API_VERSION}/private/auth",
    tags=["auth"]
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router_private.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestFormStrict = Depends()):
    data = {"username": form_data.username, "password": form_data.password}
    async with httpx.AsyncClient() as client:
        response = await client.post(CORE_LOGIN_URL, json=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    token_data = response.json()
    token = token_data.get("key")  # Token de Django Rest Auth
    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener token de Django"
        )
    return TokenResponse(access_token=token)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
import httpx
from core.config import ROOT_PATH,API_VERSION

DJANGO_USER_URL = "http://core:8080/rest-auth/user/"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{ROOT_PATH}{API_VERSION}/private/auth/login")

async def get_current_superuser(token: str = Depends(oauth2_scheme)):
    # Validar token llamando a backend Django o con lógica local
    async with httpx.AsyncClient() as client:
        response = await client.get(
            DJANGO_USER_URL,
            headers={"Authorization": f"Token {token}"}
        )
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o usuario no autenticado")

    user_data = response.json()
    if not user_data.get("is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere usuario superusuario")

    return user_data
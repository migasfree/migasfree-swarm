from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
import httpx
from core.config import ROOT_PATH, API_VERSION, CORE_USER_URL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{ROOT_PATH}{API_VERSION}/private/auth/login")

async def get_current_superuser(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            CORE_USER_URL,
            headers={"Authorization": f"Token {token}"}
        )
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or unauthenticated user")

    user_data = response.json()
    if not user_data.get("is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privileges required")

    return user_data
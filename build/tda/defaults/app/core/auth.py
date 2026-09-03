"""
Migasfree Core Staff Authentication and Token Cache
"""
import time
import logging
import httpx
from fastapi import Request, HTTPException, status
from core.config import CORE_USER_URL, logger

# Short in-memory token cache (TTL: 10 seconds) to avoid spamming Core during polling
_AUTH_CACHE: dict[str, tuple[dict, float]] = {}
AUTH_CACHE_TTL = 10.0


async def get_core_staff_user(request: Request) -> dict:
    """
    Authenticate user against Migasfree Core (Django) and ensure is_staff or is_superuser.
    Extracts token from:
      1. Cookie 'mf_token' or 'tda_token' or 'auth_token'
      2. Header 'Authorization: Bearer <token>' or 'Authorization: Token <token>'
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() in ("bearer", "token"):
            token = parts[1]

    if not token:
        token = request.cookies.get("mf_token") or request.cookies.get("tda_token") or request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = time.time()
    if token in _AUTH_CACHE:
        cached_user, timestamp = _AUTH_CACHE[token]
        if now - timestamp < AUTH_CACHE_TTL:
            return cached_user

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                CORE_USER_URL,
                headers={"Authorization": f"Token {token}"}
            )

        if resp.status_code != 200:
            _AUTH_CACHE.pop(token, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = resp.json()
        is_staff = user_data.get("is_staff", False)
        is_superuser = user_data.get("is_superuser", False)

        if not (is_staff or is_superuser):
            _AUTH_CACHE.pop(token, None)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff privileges required to access TDA service",
            )

        _AUTH_CACHE[token] = (user_data, now)
        return user_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating token with Migasfree Core: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to verify authentication with Core: {e}",
        )

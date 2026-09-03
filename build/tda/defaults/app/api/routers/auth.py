"""
Authentication Endpoints
"""
import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.responses import JSONResponse
from core.config import CORE_LOGIN_URL, CORE_USER_URL
from core.auth import get_core_staff_user
from api.models import LoginRequest

logger = logging.getLogger("migasfree-tda")
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(login_req: LoginRequest, response: Response):
    """
    Authenticate against Django rest-auth and set secure cookie.
    Only allows users with is_staff or is_superuser.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            auth_resp = await client.post(
                CORE_LOGIN_URL,
                json={"username": login_req.username, "password": login_req.password},
            )

        if auth_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token_data = auth_resp.json()
        token = token_data.get("key") or token_data.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token not returned by Core",
            )

        # Validate staff permissions
        async with httpx.AsyncClient(timeout=10.0) as client:
            user_resp = await client.get(
                CORE_USER_URL,
                headers={"Authorization": f"Token {token}"}
            )

        if user_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to fetch user profile")

        user_data = user_resp.json()
        if not (user_data.get("is_staff") or user_data.get("is_superuser")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff or superuser privileges required to access TDA Dashboard",
            )

        res = JSONResponse(content={
            "status": "success",
            "token": token,
            "user": {
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "is_staff": user_data.get("is_staff"),
                "is_superuser": user_data.get("is_superuser"),
            }
        })
        res.set_cookie(
            key="tda_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/",
            max_age=86400 * 7,
        )
        return res

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout():
    """Clear the session cookie."""
    res = JSONResponse(content={"status": "logged_out"})
    res.delete_cookie(key="tda_token", path="/")
    res.delete_cookie(key="mf_token", path="/")
    res.delete_cookie(key="auth_token", path="/")
    return res


@router.get("/me")
async def current_user(user: dict = Depends(get_core_staff_user)):
    """Return currently authenticated staff user info."""
    return JSONResponse(content={
        "username": user.get("username"),
        "email": user.get("email"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "is_staff": user.get("is_staff"),
        "is_superuser": user.get("is_superuser"),
    })

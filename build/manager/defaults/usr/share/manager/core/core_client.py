import asyncio
import httpx
from fastapi import HTTPException

from core.config import STACK, CORE_TOKEN_URL, CORE_AUTH_URL


def get_token_superuser():
    with open(f'/run/secrets/{STACK}_superadmin_name', 'r') as f:
        SUPERADMIN_NAME = f.read()
    with open(f'/run/secrets/{STACK}_superadmin_pass', 'r') as f:
        SUPERADMIN_PASS = f.read()
    data = {"username": SUPERADMIN_NAME, "password": SUPERADMIN_PASS}
    headers = {"Content-Type": "application/json"}
    response = httpx.post(CORE_AUTH_URL, json=data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Invalid credentials")
    tokens = response.json()
    token = tokens.get("token")
    if not token:
        raise HTTPException(status_code=500, detail="Token not found in response")
    return token


TOKEN = get_token_superuser()


async def get_project_info(name: str = None):
    headers = {"accept": "application/json", "Authorization": f"Token {TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CORE_TOKEN_URL}/projects/", headers=headers, follow_redirects=False)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching projects")
    data = response.json()
    projects = data.get("results", [])
    project = None
    if name:
        for p in projects:
            if p.get("name") == name:
                project = p
                break
    else:
        project = projects[0] if projects else None
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
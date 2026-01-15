import asyncio

import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer

from core.config import (
    ROOT_PATH,
    API_VERSION,
    STACK,
    CORE_TOKEN_URL,
    CORE_AUTH_URL,
    CORE_USER_URL,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{ROOT_PATH}{API_VERSION}/private/auth/login"
)

TOKEN = None


def get_token_user(username: str, password: str):
    data = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    response = httpx.post(CORE_AUTH_URL, json=data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Invalid credentials"
        )
    tokens = response.json()
    token = tokens.get("token")
    if not token:
        raise HTTPException(status_code=500, detail="Token not found in response")
    return token


def get_token_superuser():
    with open(f"/run/secrets/{STACK}_superadmin_name", "r") as f:
        SUPERADMIN_NAME = f.read()
    with open(f"/run/secrets/{STACK}_superadmin_pass", "r") as f:
        SUPERADMIN_PASS = f.read()
    return get_token_user(SUPERADMIN_NAME, SUPERADMIN_PASS)


def get_cached_token():
    global TOKEN
    if TOKEN is None:
        TOKEN = get_token_superuser()
    return TOKEN


async def get_current_superuser(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            CORE_USER_URL, headers={"Authorization": f"Token {token}"}
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or unauthenticated user",
        )

    user_data = response.json()
    if not user_data.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )

    return user_data


async def get_core_user(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            CORE_USER_URL, headers={"Authorization": f"Token {token}"}
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or unauthenticated user",
        )
    user_data = response.json()
    return user_data


async def get_project_info(name: str = None):
    token = get_cached_token()
    headers = {"accept": "application/json", "Authorization": f"Token {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CORE_TOKEN_URL}/projects/", headers=headers, follow_redirects=False
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Error fetching projects"
        )
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


async def get_groups_info():
    token = get_cached_token()
    headers = {"accept": "application/json", "Authorization": f"Token {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CORE_TOKEN_URL}/accounts/groups/",
            headers=headers,
            follow_redirects=False,
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Error fetching groups"
        )
    data = response.json()
    groups = data.get("results", [])
    return groups


def group_has_permission(
    groups: list, group_name: str, permission_codename: str
) -> bool:
    """
    Check if a specific group has a given permission.

    Args:
        groups: List of groups with their permissions
        group_name: Name of the group to search for (e.g., 'Reader')
        permission_codename: Codename of the permission to search for (e.g., 'add_computer')

    Returns:
        True if the group has the permission, False otherwise
    """
    # Find the group by name
    group = next((g for g in groups if g.get("name") == group_name), None)

    if group is None:
        return False

    # Check if the permission exists in the group's permissions
    permissions = group.get("permissions", [])
    return any(perm.get("codename") == permission_codename for perm in permissions)


async def user_has_permission(user_data: dict, codename: str) -> bool:
    """
    Check if a user has a specific permission either directly or through their groups.

    This function searches for a permission in two places:
    1. Direct user permissions (user_permissions)
    2. Permissions inherited from user's groups

    Args:
        user_data: Dictionary containing user information with the following structure:
            - user_permissions (list, optional): List of permission dictionaries,
              each containing a 'codename' key
            - groups (list, optional): List of group dictionaries,
              each containing a 'name' key
        codename: The permission codename to search for (e.g., 'add_computer', 'delete_user')

    Returns:
        bool: True if the user has the permission (directly or through a group),
              False otherwise

    Examples:
        >>> user = {
        ...     "user_permissions": [{"codename": "view_data"}],
        ...     "groups": [{"name": "Editors"}]
        ... }
        >>> await user_has_permission(user, "view_data")
        True

    Note:
        This is an async function that calls get_groups_info() to retrieve
        group information from the system.
    """
    # Check if the permission exists in the guser
    user_permissions = user_data.get("user_permissions", [])
    for permission in user_permissions:
        if permission.get("codename") == codename:
            return True
    # Find the group by name
    groups = await get_groups_info()
    for group in user_data.get("groups", []):
        if group_has_permission(groups, group["name"], codename):
            return True
    return False

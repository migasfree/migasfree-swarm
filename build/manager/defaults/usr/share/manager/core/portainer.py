import logging
import asyncio
from dataclasses import dataclass

import httpx

from core.upgrade import get_image_list

logger = logging.getLogger(__name__)

PORTAINER_BASE_URL = "http://portainer:9000"
PORTAINER_AUTH_TIMEOUT = 10
PULL_TIMEOUT = 600  # 10 minutes max per image pull


@dataclass
class PortainerSession:
    jwt: str
    user_id: int
    username: str
    role: int  # 1 = admin, 2 = standard user


@dataclass
class PullProgress:
    node: str
    image: str
    status: str  # "pulling", "done", "skipped", "error"
    detail: str = ""


async def authenticate(username: str, password: str) -> PortainerSession:
    """
    Authenticate against Portainer API and return a session with JWT.

    Raises:
        httpx.HTTPStatusError: if authentication fails (401/422).
        PermissionError: if the user is not an administrator (Role != 1).
        ConnectionError: if Portainer is unreachable.
    """
    try:
        async with httpx.AsyncClient(
            base_url=PORTAINER_BASE_URL,
            timeout=PORTAINER_AUTH_TIMEOUT,
        ) as client:
            # Step 1: Authenticate and obtain JWT
            auth_response = await client.post(
                "/api/auth",
                json={"username": username, "password": password},
            )
            auth_response.raise_for_status()
            jwt_token = auth_response.json().get("jwt", "")

            if not jwt_token:
                raise ValueError("Portainer returned empty JWT")

            # Step 2: Verify the user has admin role
            headers = {"Authorization": f"Bearer {jwt_token}"}
            me_response = await client.get("/api/users/me", headers=headers)
            me_response.raise_for_status()

            user_data = me_response.json()
            user_id = user_data.get("Id", 0)
            role = user_data.get("Role", 0)

            if role != 1:
                raise PermissionError(
                    f"User '{username}' is not a Portainer administrator "
                    f"(Role={role}, expected 1)"
                )

            logger.info(
                f"Portainer authentication successful for user '{username}' "
                f"(userId={user_id}, role=admin)"
            )

            return PortainerSession(
                jwt=jwt_token,
                user_id=user_id,
                username=username,
                role=role,
            )

    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 422:
            logger.warning(
                f"Portainer auth failed for user '{username}': Invalid credentials (422)"
            )
            raise PermissionError("Invalid username or password.")
        if status in (401, 403):
            logger.warning(
                f"Portainer auth failed for user '{username}': HTTP {status}"
            )
            raise PermissionError("Access denied or invalid credentials.")
        logger.error(f"Portainer API error: HTTP {status}")
        raise
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to Portainer at {PORTAINER_BASE_URL}: {e}")
        raise ConnectionError(
            f"Cannot connect to Portainer at {PORTAINER_BASE_URL}"
        ) from e


async def _get_endpoint_id(client: httpx.AsyncClient, headers: dict) -> int:
    """Get the Portainer endpoint ID for 'primary'."""
    response = await client.get("/api/endpoints", headers=headers)
    response.raise_for_status()
    for endpoint in response.json():
        if endpoint.get("Name") == "primary":
            return endpoint["Id"]
    raise ValueError("Portainer endpoint 'primary' not found")


async def _get_nodes(
    client: httpx.AsyncClient, headers: dict, endpoint_id: int
) -> list[dict]:
    """Get all active Swarm nodes via Portainer Docker proxy."""
    response = await client.get(
        f"/api/endpoints/{endpoint_id}/docker/nodes",
        headers=headers,
    )
    response.raise_for_status()
    nodes = []
    for node in response.json():
        status = node.get("Status", {}).get("State", "")
        availability = node.get("Spec", {}).get("Availability", "")
        if status == "ready" and availability == "active":
            hostname = node.get("Description", {}).get("Hostname", "unknown")
            nodes.append({
                "id": node["ID"],
                "hostname": hostname,
                "role": node.get("Spec", {}).get("Role", "worker"),
            })
    return nodes


async def _pull_image_on_node(
    client: httpx.AsyncClient,
    headers: dict,
    endpoint_id: int,
    image: str,
    node_name: str,
) -> tuple[str, str]:
    """
    Pull a single image via Portainer Docker proxy endpoint.

    Uses POST /api/endpoints/{id}/docker/images/create?fromImage=...
    Returns: (status, detail) where status is "done", "skipped", or "error"
    """
    image_name, image_tag = image.rsplit(":", 1)

    node_headers = dict(headers)
    node_headers["X-PortainerAgent-Target"] = node_name

    # Check if image already exists
    try:
        inspect_response = await client.get(
            f"/api/endpoints/{endpoint_id}/docker/images/{image}/json",
            headers=node_headers,
            timeout=10,
        )
        if inspect_response.status_code == 200:
            return "skipped", ""
    except Exception:
        pass  # Image doesn't exist, proceed with pull

    # Pull the image
    try:
        pull_response = await client.post(
            f"/api/endpoints/{endpoint_id}/docker/images/create",
            headers=node_headers,
            params={"fromImage": image_name, "tag": image_tag},
            timeout=PULL_TIMEOUT,
        )
        if pull_response.status_code == 200:
            return "done", ""
        else:
            try:
                err_data = pull_response.json()
                err_msg = err_data.get("message") or err_data.get("details") or str(err_data)
            except Exception:
                err_msg = pull_response.text.strip() or f"HTTP {pull_response.status_code}"
            logger.warning(f"Pull failed for {image}: {err_msg}")
            return "error", err_msg
    except httpx.TimeoutException:
        logger.error(f"Timeout pulling {image}")
        return "error", "Request timed out"
    except Exception as e:
        logger.error(f"Error pulling {image}: {e}")
        return "error", str(e)


async def pull_images_on_all_nodes(
    session: PortainerSession,
    version: str,
    progress_callback=None,
):
    """
    Pull all migasfree images for a given version on every Swarm node.

    Args:
        session: Authenticated PortainerSession with JWT.
        version: Target version string (e.g., "5.1.0").
        progress_callback: Optional async callable(PullProgress) for SSE events.

    Returns:
        dict with summary: {"total_images", "total_nodes", "results": [...]}
    """
    images = get_image_list(version)
    headers = {"Authorization": f"Bearer {session.jwt}"}
    results = []

    async with httpx.AsyncClient(
        base_url=PORTAINER_BASE_URL,
        timeout=30,
    ) as client:
        # Get the primary endpoint
        endpoint_id = await _get_endpoint_id(client, headers)

        # Get all active nodes
        nodes = await _get_nodes(client, headers, endpoint_id)
        logger.info(
            f"Pulling {len(images)} images on {len(nodes)} nodes "
            f"for version {version}"
        )

        # Pull images on each node
        for node in nodes:
            node_name = node["hostname"]
            for image in images:
                progress = PullProgress(
                    node=node_name,
                    image=image,
                    status="pulling",
                )
                if progress_callback:
                    await progress_callback(progress)

                status, detail = await _pull_image_on_node(
                    client, headers, endpoint_id, image, node_name
                )
                progress.status = status
                progress.detail = detail
                if progress_callback:
                    await progress_callback(progress)

                results.append({
                    "node": node_name,
                    "image": image,
                    "status": status,
                    "detail": detail,
                })

    summary = {
        "version": version,
        "total_images": len(images),
        "total_nodes": len(nodes),
        "nodes": [n["hostname"] for n in nodes],
        "results": results,
        "all_ok": all(r["status"] in ("done", "skipped") for r in results),
    }

    if summary["all_ok"]:
        logger.info(
            f"All {len(images)} images for version {version} are ready"
        )
    else:
        failed = [r["image"] for r in results if r["status"] == "error"]
        logger.warning(
            f"{len(failed)} images failed to pull: {failed}"
        )

    return summary

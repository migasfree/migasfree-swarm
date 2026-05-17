import logging
import httpx
import yaml
from fastapi import APIRouter, HTTPException, status
from core.config import MCI_TEMPLATES_URL, API_VERSION

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_VERSION}/internal/mci",
    tags=["mci"],
)

async def _fetch_text(url: str) -> str:
    logger.debug(f"Fetching text from URL: {url}")
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.text

@router.get("/catalog")
async def get_mci_catalog():
    """Fetch the MCI templates catalog."""
    base_url = MCI_TEMPLATES_URL.rstrip("/")
    url = f"{base_url}/catalog.yml"
    try:
        content = await _fetch_text(url)
        return yaml.safe_load(content)
    except Exception as e:
        logger.error(f"Error fetching MCI catalog: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch catalog: {str(e)}"
        )

@router.get("/templates/{template_id:path}")
async def get_mci_template(
    template_id: str,
):
    """Fetch the full content of a specific MCI template."""
    base_url = MCI_TEMPLATES_URL.rstrip("/")
    catalog_url = f"{base_url}/catalog.yml"
    try:
        catalog_content = await _fetch_text(catalog_url)
        logger.debug(f"Catalog content received: {catalog_content[:200]}...")
        catalog = yaml.safe_load(catalog_content)

        if not isinstance(catalog, dict):
            logger.error(f"Catalog is not a dictionary: {type(catalog)}")
            raise HTTPException(status_code=500, detail="Invalid catalog format")

        template_info = next((t for t in catalog.get("templates", []) if t.get("id") == template_id), None)
        if not template_info:
            raise HTTPException(status_code=404, detail="Template not found")
        
        base_path = f"{base_url}/{template_info['path']}"
        
        dockerfile = await _fetch_text(f"{base_path}/dockerfile.j2")
        partition = await _fetch_text(f"{base_path}/partition.yml")
        
        # deployments.yml is optional
        deployments = None
        try:
            deployments = await _fetch_text(f"{base_path}/deployments.yml")
        except Exception:
            pass

        return {
            "id": template_id,
            "base_os": template_info.get("base_os"),
            "dockerfile": dockerfile,
            "partition": partition,
            "deployments": deployments
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch template details: {str(e)}"
        )

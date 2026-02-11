import logging
import requests

logger = logging.getLogger("migasfree-mcp")

# Internal service URLs
_SERVICE_URLS = {
    "core": "http://core:80/api/schema/",
    "manager": "http://manager:8080/openapi.json",
}

# API schema cache: loaded once per service, reused forever (only changes on redeploy)
_api_cache = {}


def get_api_schema(service: str):
    """Returns the OpenAPI schema for a service (cached in memory after first call)."""
    if service in _api_cache:
        return _api_cache[service]

    url = _SERVICE_URLS.get(service)
    if not url:
        return {
            "ERROR": f"Unknown service: '{service}'. Valid: {list(_SERVICE_URLS.keys())}"
        }

    logger.info(f"Loading API schema for '{service}' into cache...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        schema = response.json()
        _api_cache[service] = schema
        return schema
    except Exception as e:
        logger.warning(f"Failed to fetch schema from {url}: {e}")
        return {"ERROR": f"Failed to fetch schema from {service}: {str(e)}"}


def clear_api_cache(service: str | None = None):
    """Clear cached API schema(s). Pass service name or None for all."""
    if service:
        _api_cache.pop(service, None)
        logger.info(f"API schema cache cleared for '{service}'")
    else:
        _api_cache.clear()
        logger.info("API schema cache cleared (all services)")

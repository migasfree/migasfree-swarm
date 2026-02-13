import logging
import requests
from pathlib import Path

logger = logging.getLogger("migasfree-mcp")

# Internal service URLs
_SERVICE_URLS = {
    # Core (Django) defaults to YAML, so we explicitly request JSON format
    "core": "http://core:8080/api/schema/?format=json",
    # Manager (FastAPI) serves JSON by default
    "manager": "http://manager:8080/openapi.json",
}

# API schema cache: loaded once per service, reused forever (only changes on redeploy)
_api_cache = {}


def get_api_schema(service: str, tag: str | None = None):
    """Returns the OpenAPI schema for a service (cached in memory after first call)."""
    if service in _api_cache:
        schema = _api_cache[service]
    else:
        url = _SERVICE_URLS.get(service)
        if not url:
            return {
                "ERROR": f"Unknown service: '{service}'. Valid: {list(_SERVICE_URLS.keys())}"
            }

        logger.info(f"Loading API schema for '{service}' into cache...")
        try:
            response = requests.get(
                url, headers={"Accept": "application/json"}, timeout=30
            )
            response.raise_for_status()
            schema = response.json()
            _api_cache[service] = schema
        except Exception as e:
            logger.warning(f"Failed to fetch schema from {url}: {e}")
            return {"ERROR": f"Failed to fetch schema from {service}: {str(e)}"}

    # If a tag is specified, filter the schema
    if tag:
        filtered_paths = {}
        for path, methods in schema.get("paths", {}).items():
            for method, details in methods.items():
                if isinstance(details, dict) and tag in details.get("tags", []):
                    if path not in filtered_paths:
                        filtered_paths[path] = {}
                    filtered_paths[path][method] = details

        return {
            "openapi": schema.get("openapi"),
            "info": schema.get("info"),
            "paths": filtered_paths,
            "components": schema.get(
                "components", {}
            ),  # Keep all components for simplicity
            "note": f"Filtered by tag: '{tag}'",
        }

    # If no tag is specified and the schema is large, return a summary
    # 100 paths is a safe threshold for MCP/LLM context
    if len(schema.get("paths", {})) > 100:
        return {
            "info": schema.get("info"),
            "tags": [t.get("name") for t in schema.get("tags", [])],
            "total_paths": len(schema.get("paths", {})),
            "available_paths": list(schema.get("paths", {}).keys()),
            "usage_tip": "The schema is large. Use the 'tag' argument to get full details for a specific group of endpoints.",
        }

    return schema


def openapi_to_markdown(schema: dict) -> str:
    """Simple converter from OpenAPI JSON to Markdown for LLM readability."""
    info = schema.get("info", {})
    md = [f"# {info.get('title', 'API Reference')}\n"]
    md.append(f"**Version**: {info.get('version', 'N/A')}\n")
    if info.get("description"):
        md.append(f"{info.get('description')}\n")

    paths = schema.get("paths", {})
    for path, methods in sorted(paths.items()):
        md.append(f"\n## Endpoint: {path}")
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            summary = details.get("summary", "")
            description = details.get("description", "")
            tags = ", ".join(details.get("tags", []))

            md.append(f"### {method.upper()}")
            if tags:
                md.append(f"*Tags: {tags}*")
            if summary:
                md.append(f"\n**Summary**: {summary}")
            if description:
                md.append(f"\n{description}")

            # Parameters
            params = details.get("parameters", [])
            if params:
                md.append("\n#### Parameters")
                for p in params:
                    pname = p.get("name")
                    pin = p.get("in")
                    pdesc = p.get("description", "")
                    preq = " (required)" if p.get("required") else ""
                    md.append(f"- `{pname}` ({pin}): {pdesc}{preq}")

            # Request Body
            content = details.get("requestBody", {}).get("content", {})
            if "application/json" in content:
                schema_info = content["application/json"].get("schema", {})
                md.append("\n#### Request Body (JSON)")
                if "$ref" in schema_info:
                    md.append(f"- Schema Ref: `{schema_info.get('$ref')}`")
                elif "properties" in schema_info:
                    md.append("- Properties:")
                    for prop, pdetails in schema_info.get("properties", {}).items():
                        ptype = pdetails.get("type", "any")
                        md.append(f"  - `{prop}` ({ptype})")

        md.append("\n---")
    return "\n".join(md)


def sync_api_to_files(docs_dir: str) -> bool:
    """Downloads all schemas and saves them as Markdown in the docs directory."""
    docs_path = Path(docs_dir)
    docs_path.mkdir(parents=True, exist_ok=True)
    success = True

    for name, url in _SERVICE_URLS.items():
        try:
            logger.info(f"Syncing API schema for '{name}' to file...")
            response = requests.get(
                url, headers={"Accept": "application/json"}, timeout=30
            )
            response.raise_for_status()
            schema = response.json()

            # Save Markdown version
            md_content = openapi_to_markdown(schema)
            md_path = docs_path / f"api_{name}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            logger.info(f"API schema for '{name}' saved to {md_path}")
        except Exception as e:
            logger.error(f"Failed to sync API schema for '{name}': {e}")
            success = False

    return success


def clear_api_cache(service: str | None = None):
    """Clear cached API schema(s). Pass service name or None for all."""
    if service:
        _api_cache.pop(service, None)
        logger.info(f"API schema cache cleared for '{service}'")
    else:
        _api_cache.clear()
        logger.info("API schema cache cleared (all services)")

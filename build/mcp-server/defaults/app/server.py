import json
import os
import logging
import contextlib
import anyio
from collections.abc import AsyncIterator
from typing import Any
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ResourceTemplate,
    GetPromptResult,
    PromptMessage,
)
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from database import run_sql_select_query, get_db_schema
from api import get_api_schema
from docs import get_manual_content
from resources import read_file
from settings import VERSION, DEBUG, CORPUS_PATH_DOCS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("migasfree-mcp")

# MCP Server definition
app = Server("migasfree-mcp-server")


# ==============================================================================
# Tools
# ==============================================================================


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="db_query",
            description="Execute a SELECT SQL query on the PostgreSQL database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The exact SQL SELECT query to execute.",
                    }
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="db_get_schema",
            description="Retrieve the complete database schema.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="api_get_schema",
            description="Get the OpenAPI/Swagger schema for Migasfree services.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "enum": ["core", "manager"],
                    }
                },
                "required": ["service"],
            },
        ),
        Tool(
            name="docs_get_manual",
            description="Get the full content of the Migasfree user manual.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    try:
        if name == "db_query":
            sql = arguments.get("sql", "")
            result = run_sql_select_query(sql)
            return [
                TextContent(type="text", text=json.dumps(result, indent=2, default=str))
            ]
        elif name == "db_get_schema":
            result = get_db_schema()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        elif name == "api_get_schema":
            service = arguments.get("service")
            result = get_api_schema(service)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        elif name == "docs_get_manual":
            result = get_manual_content()
            return [TextContent(type="text", text=result)]
        return [TextContent(type="text", text=f"Tool unknown: {name}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ==============================================================================
# Resources
# ==============================================================================


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available static resources."""
    resources = []

    # Database schema resource
    resources.append(
        Resource(
            uri="migasfree://schema/database",
            name="Database Schema",
            description="Complete PostgreSQL database schema with tables and columns",
            mimeType="application/json",
        )
    )

    # Documentation resources
    if os.path.exists(CORPUS_PATH_DOCS):
        _mime_types = {
            ".md": "text/markdown",
            ".rst": "text/plain",
            ".txt": "text/plain",
            ".pdf": "application/pdf",
        }
        for filename in sorted(os.listdir(CORPUS_PATH_DOCS)):
            ext = os.path.splitext(filename)[1].lower()
            if ext in _mime_types:
                resources.append(
                    Resource(
                        uri=f"migasfree://docs/{filename}",
                        name=f"Doc: {filename}",
                        description=f"Documentation file: {filename}",
                        mimeType=_mime_types[ext],
                    )
                )

    return resources


@app.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """List resource templates for dynamic resources."""
    return [
        ResourceTemplate(
            uriTemplate="migasfree://api/{service}/schema",
            name="API Schema",
            description="OpenAPI schema for a Migasfree service (core or manager)",
            mimeType="application/json",
        ),
    ]


@app.read_resource()
async def read_resource(uri) -> str:
    """Read a specific resource by URI."""
    uri = str(uri)  # MCP SDK sends AnyUrl, convert to string
    logger.info(f"Reading resource: {uri}")

    if uri == "migasfree://schema/database":
        schema = get_db_schema()
        return json.dumps(schema, indent=2)

    if uri.startswith("migasfree://docs/"):
        filename = uri.replace("migasfree://docs/", "")
        path = os.path.join(CORPUS_PATH_DOCS, filename)
        if os.path.isfile(path):
            if filename.lower().endswith(".pdf"):
                from docs import _read_pdf

                return _read_pdf(path)
            return read_file(path)
        return f"File not found: {filename}"

    if uri.startswith("migasfree://api/"):
        # e.g. migasfree://api/core/schema
        parts = uri.replace("migasfree://api/", "").split("/")
        if len(parts) >= 1:
            service = parts[0]
            schema = get_api_schema(service)
            return json.dumps(schema, indent=2)

    return f"Unknown resource: {uri}"


# ==============================================================================
# Prompts
# ==============================================================================


@app.list_prompts()
async def list_prompts() -> list[dict]:
    """List available prompt templates."""
    return [
        {
            "name": "analyze_fleet",
            "description": "Analyze the computer fleet: status distribution, projects, sync activity",
            "arguments": [],
        },
        {
            "name": "find_sync_errors",
            "description": "Find computers with synchronization errors or issues",
            "arguments": [],
        },
        {
            "name": "query_builder",
            "description": "Help build a SQL query for the Migasfree database",
            "arguments": [
                {
                    "name": "question",
                    "description": "What data do you want to find? (natural language)",
                    "required": True,
                },
            ],
        },
    ]


@app.get_prompt()
async def get_prompt(
    name: str, arguments: dict[str, str] | None = None
) -> GetPromptResult:
    """Get a specific prompt by name."""
    logger.info(f"Getting prompt: {name}")

    if name == "analyze_fleet":
        return GetPromptResult(
            description="Analyze the Migasfree computer fleet",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            "Analyze the Migasfree computer fleet. Use the db_get_schema tool first "
                            "to understand the database structure, then run these queries:\n\n"
                            "1. Total computers by status (productive, intended, reserved, unsubscribed)\n"
                            "2. Computers per project\n"
                            "3. Last synchronization dates\n"
                            "4. Computers that haven't synced in over 7 days\n\n"
                            "Present the results with a clear summary and any concerns."
                        ),
                    ),
                )
            ],
        )

    elif name == "find_sync_errors":
        return GetPromptResult(
            description="Find synchronization errors in Migasfree",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            "Find computers with synchronization problems. Use the db_get_schema tool "
                            "to understand the database, then check:\n\n"
                            "1. Computers where sync_end_date is NULL (incomplete syncs)\n"
                            "2. Computers not synced in the last 30 days\n"
                            "3. Any error records in the system\n\n"
                            "Provide actionable recommendations for each issue found."
                        ),
                    ),
                )
            ],
        )

    elif name == "query_builder":
        question = (arguments or {}).get("question", "")
        return GetPromptResult(
            description="Build a SQL query for Migasfree",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"I need help querying the Migasfree database. My question is:\n\n"
                            f'"{question}"\n\n'
                            "First, use db_get_schema to understand the database structure. "
                            "Then build and execute the appropriate SQL query. "
                            "Explain what the query does and present the results clearly."
                        ),
                    ),
                )
            ],
        )

    raise ValueError(f"Unknown prompt: {name}")


# ==============================================================================
# SSE Transport (legacy clients)
# ==============================================================================
sse = SseServerTransport("/messages")


def _get_init_options():
    return InitializationOptions(
        server_name="migasfree-mcp-server",
        server_version=VERSION,
        capabilities=app.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )


async def sse_router(scope, receive, send):
    """Handle legacy SSE transport at /mcp/sse and /mcp/messages."""
    path = scope.get("path", "")
    root_path = scope.get("root_path", "")
    logger.info(f"SSE Router received path: '{path}', root_path: '{root_path}'")
    if path in ["/sse", "/mcp/sse"]:
        logger.info("New SSE connection established")
        try:
            async with sse.connect_sse(scope, receive, send) as (read, write):
                await app.run(read, write, _get_init_options())
        except anyio.get_cancelled_exc_class():
            logger.info("SSE connection cancelled (client disconnected)")
        except Exception:
            logger.exception("Error in handle_sse")
        finally:
            logger.info("SSE connection closed")
    elif path in ["/messages", "/mcp/messages"]:
        try:
            await sse.handle_post_message(scope, receive, send)
        except Exception:
            logger.error("Exception in handle_messages (caught to prevent crash)")
    else:
        response = Response("Not Found", status_code=404)
        await response(scope, receive, send)


# ==============================================================================
# Streamable HTTP Transport (modern clients like Antigravity)
# ==============================================================================
session_manager = StreamableHTTPSessionManager(
    app=app,
    stateless=False,
    json_response=False,
)


# ==============================================================================
# Unified MCP Router
# ==============================================================================


async def mcp_router(scope, receive, send):
    """
    Unified MCP router that detects transport type and dispatches accordingly.

    Detection logic:
    - POST with Content-Type: application/json -> Streamable HTTP
    - GET/DELETE with mcp-session-id header -> Streamable HTTP
    - GET on /sse path -> SSE (legacy)
    - POST on /messages path -> SSE messages (legacy)
    """
    path = scope.get("path", "")
    request = Request(scope, receive)
    method = request.method
    content_type = request.headers.get("content-type", "")
    has_session_id = "mcp-session-id" in request.headers

    logger.info(
        f"MCP Router: method={method}, path='{path}', "
        f"content_type='{content_type}', has_session_id={has_session_id}"
    )

    # Path-based routing for legacy SSE endpoints
    if path in ["/messages", "/mcp/messages"]:
        logger.info("Routing to SSE legacy (messages endpoint)")
        await sse_router(scope, receive, send)
        return

    # For /sse path, detect transport type
    if path in ["/sse", "/mcp/sse", "/", ""]:
        # Streamable HTTP: POST with JSON body
        if method == "POST" and "application/json" in content_type:
            logger.info("Routing to Streamable HTTP (POST with JSON)")
            await session_manager.handle_request(scope, receive, send)
        # Streamable HTTP: GET or DELETE with session header
        elif method in ("GET", "DELETE") and has_session_id:
            logger.info(f"Routing to Streamable HTTP ({method} with session)")
            await session_manager.handle_request(scope, receive, send)
        # Legacy SSE: GET without session header (SSE stream init)
        elif method == "GET":
            logger.info("Routing to SSE legacy (GET /sse)")
            await sse_router(scope, receive, send)
        # Legacy SSE: POST without JSON content type
        elif method == "POST":
            logger.info("Routing to SSE legacy (POST /sse)")
            await sse_router(scope, receive, send)
        else:
            response = Response("Method Not Allowed", status_code=405)
            await response(scope, receive, send)
    else:
        response = Response("Not Found", status_code=404)
        await response(scope, receive, send)


# ==============================================================================
# Main App with lifespan
# ==============================================================================


@contextlib.asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    """Application lifespan that manages the Streamable HTTP session manager."""
    async with session_manager.run():
        logger.info("Streamable HTTP session manager started")
        yield
    logger.info("Streamable HTTP session manager stopped")


starlette_app = FastAPI(debug=DEBUG, lifespan=lifespan)
starlette_app.mount("/mcp", mcp_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        starlette_app,
        host="0.0.0.0",
        port=8080,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )

import json
import os
import logging
import contextlib
import anyio
import asyncio
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

from database import run_sql_select_query, sync_db_to_file
from api import sync_api_to_files
from resources import read_file
from docs import convert_all_pdfs_to_markdown
from settings import VERSION, DEBUG, CORPUS_PATH_DOCS, MCP_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("migasfree-mcp")

# MCP Server definition
app = Server(f"{MCP_NAME}-mcp-server")


# ==============================================================================
# Tools
# ==============================================================================


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="db_query",
            description=f"Execute a SELECT SQL query on the PostgreSQL database. IMPORTANT: Before querying for table structure, metadata, or column names, YOU MUST READ the resource '{MCP_NAME}://docs/db_schema.md' which contains the full documented schema.",
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
        return [TextContent(type="text", text=f"Tool unknown: {name}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ==============================================================================
# Resources
# ==============================================================================


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available documentation resources."""
    resources = []

    if os.path.isdir(CORPUS_PATH_DOCS):
        # 1. Master Index (if exists)
        index_path = os.path.join(CORPUS_PATH_DOCS, "documentation_index.md")
        if os.path.isfile(index_path):
            resources.append(
                Resource(
                    uri=f"{MCP_NAME}://docs/documentation_index.md",
                    name="📚 Documentation Index",
                    description="Master index of all available Migasfree documentation.",
                    mimeType="text/markdown",
                )
            )

        # 2. Files
        _mime_types = {
            ".md": "text/markdown",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".rst": "text/plain",
        }
        for filename in sorted(os.listdir(CORPUS_PATH_DOCS)):
            if filename.startswith(".") or filename == "documentation_index.md":
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext in _mime_types:
                resources.append(
                    Resource(
                        uri=f"{MCP_NAME}://docs/{filename}",
                        name=f"Doc: {filename}",
                        description=f"Documentation file: {filename}",
                        mimeType=_mime_types[ext],
                    )
                )

    return resources


@app.list_resource_templates()
async def list_resource_templates() -> list[ResourceTemplate]:
    """List resource templates (none currently)."""
    return []


@app.read_resource()
async def read_resource(uri) -> str:
    """Read a specific resource by URI."""
    uri = str(uri)  # MCP SDK sends AnyUrl, convert to string
    logger.info(f"Reading resource: {uri}")

    if uri.startswith(f"{MCP_NAME}://docs/"):
        filename = uri.replace(f"{MCP_NAME}://docs/", "")
        path = os.path.join(CORPUS_PATH_DOCS, filename)
        if os.path.isfile(path):
            if filename == "documentation_index.md":
                content = read_file(path)
                return content.replace("{MCP_SERVER_URI}", f"{MCP_NAME}://")

            if filename.lower().endswith(".pdf"):
                from docs import _read_pdf

                return _read_pdf(path)
            return read_file(path)
        return f"File not found: {filename}"

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


async def background_doc_sync():
    """Retry syncing documentation until successful or timeout."""
    max_retries = 30  # 5 minutes approx if 10s sleep
    for i in range(max_retries):
        try:
            # Use run_sync to avoid blocking event loop
            db_success = await anyio.to_thread.run_sync(
                sync_db_to_file, CORPUS_PATH_DOCS
            )
            api_success = await anyio.to_thread.run_sync(
                sync_api_to_files, CORPUS_PATH_DOCS
            )

            if db_success and api_success:
                logger.info("Documentation sync completed successfully.")
                break

            logger.warning(
                f"Documentation sync incomplete (attempt {i + 1}/{max_retries}). Retrying in 10s..."
            )
        except Exception as e:
            logger.error(f"Error in background sync: {e}")

        await asyncio.sleep(10)


@contextlib.asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    """Application lifespan that manages the Streamable HTTP session manager."""
    try:
        # Convert PDFs immediately (local file operation)
        convert_all_pdfs_to_markdown()

        # Start background sync for DB and API docs (with retries)
        asyncio.create_task(background_doc_sync())
    except Exception as e:
        logger.error(f"Error initializing files at startup: {e}")

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

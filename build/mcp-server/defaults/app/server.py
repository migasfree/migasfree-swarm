import asyncio

from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from model import guru

from database import create_schema
from docs import create_docs
from api import create_api_categories

app = Server("migasfree-mcp-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="guru",
            description="Resuelve cualquier cuestión relacionada con migasfree en lenguaje natural, sobre su documentacion, su api o consulta de datos de la BD",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "question"
                    }
                },
                "required": ["question"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "guru":
        question = arguments.get("question", "")
        return [TextContent(
            type="text",
            text=guru(question)
        )]

    return [TextContent(type="text", text=f"Tool unknown: {name}")]


async def main():
    create_docs()
    create_schema()
    create_api_categories()

    async def run_mcp():
        async with stdio_server() as (read_stream, write_stream):
            class NotificationOptions:
                def __init__(self):
                    self.resources_changed = False
                    self.tools_changed = False
                    self.prompts_changed = False

            capabilities = app.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )

            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="migasfree-mcp-server",
                    server_version="1.0.0",
                    capabilities=capabilities
                )
            )

    await run_mcp()


if __name__ == '__main__':
    asyncio.run(main())

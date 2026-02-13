import os

# Version (single source of truth)
VERSION = "1.2.0"

STACK = os.getenv("STACK", "migasfree")
FQDN = os.getenv("FQDN", "localhost")
MCP_NAME = os.getenv("MCP_NAME", STACK)
DEBUG = os.getenv("MCP_DEBUG", "false").lower() in ("true", "1", "yes")

CORPUS_PATH_DOCS = "/app/docs"

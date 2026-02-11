#!/bin/sh

# MCP health check: verify the FastAPI + MCP server is responding
# /openapi.json returns immediately; --max-time prevents hangs
curl -sf -o /dev/null --max-time 3 http://localhost:8080/openapi.json

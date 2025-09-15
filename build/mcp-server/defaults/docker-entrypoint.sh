#!/bin/bash

update-ca-certificates

cd /app
send_message "init mcp-server"

send_message ""
sudo -E -u mcpuser mcpo --port 8080 -- python server.py

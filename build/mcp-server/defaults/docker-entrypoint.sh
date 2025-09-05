#!/bin/bash


cd /app
send_message "init mcp-server"



send_message ""
mcpo --port 8080 -- python server.py
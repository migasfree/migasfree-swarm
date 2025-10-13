#!/bin/sh

PROCESS_NAME="uvicorn main:app"

if pgrep -f "$PROCESS_NAME" > /dev/null
then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80/ca/health || echo "000")
    if [ "$HTTP_CODE" == "200" ]; then
        exit 0
    else
        exit 2
    fi
else
    exit 1
fi
#!/bin/sh

_ROOT="/srv"

PORT=${FB_PORT:-$(jq .port /.filebrowser.json)}

timeout 2 ls ${_ROOT}/conf/ >/dev/null
if [ $? -eq 0 ]
then
    curl -f http://localhost:$PORT/health
else
    echo "$(date) File system disconnected"
    exit 1
fi

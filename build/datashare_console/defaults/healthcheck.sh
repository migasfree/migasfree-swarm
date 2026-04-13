#!/bin/sh
. /usr/bin/common.sh
_ROOT="/srv"
PORT="${FB_PORT:-$(jq .port /.filebrowser.json)}"

if ! timeout 2 ls "${_ROOT}/conf/" >/dev/null
then
    echo "$(date) File system disconnected"
    exit 1
fi

check_http "http://localhost:$PORT/health"

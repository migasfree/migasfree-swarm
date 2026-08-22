#!/bin/sh
. /usr/bin/common.sh
_ROOT="/srv"
PORT="${FB_PORT:-80}"

if ! timeout 2 ls "${_ROOT}/conf/" >/dev/null 2>&1
then
    echo "$(date) File system disconnected"
    exit 1
fi

check_http "http://127.0.0.1:$PORT/"

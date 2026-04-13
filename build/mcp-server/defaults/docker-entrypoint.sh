#!/bin/sh
set -e

. /usr/bin/common.sh

if [ "$(id -u)" = '0' ]
then
    set_tz
    start_message
    update-ca-certificates
    exec gosu mcpuser "$0" "$@"
fi

cd /app || exit 1

show_banner "$(pip freeze|grep mcp)"

send_message ""

python server.py

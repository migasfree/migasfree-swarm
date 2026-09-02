#!/bin/sh
set -e

. /usr/bin/common.sh

if [ "$(id -u)" = '0' ]
then
    set_tz
    start_message
    update-ca-certificates 2>/dev/null || true
    chown -R tdauser:tdauser /data/tda
    exec gosu tdauser "$0" "$@"
fi

show_banner "TDA Analytics Service"

send_message "Waiting for database service..."
wait_for_service "${POSTGRES_HOST:-database}" "${POSTGRES_PORT:-5432}"

send_message "Starting TDA Web Service on port 8000..."

exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

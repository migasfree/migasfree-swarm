#!/bin/sh
set -e

. /usr/bin/common.sh

if [ "$(id -u)" = '0' ]
then
    set_tz
    start_message
    exec gosu migasfree "$0" "$@"
fi

send_message "waiting datastore"
wait_for_service "datastore" "6379"

load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
REDIS_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"
export REDIS_URL

show_banner "$(python3 --version)"

send_message ""

exec python3 -u main.py

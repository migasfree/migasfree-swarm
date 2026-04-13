#!/bin/sh

. /usr/bin/common.sh
set_tz

MIGASFREE_SECRET_DIR='/var/run/secrets'
load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
REDIS_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"
export REDIS_URL
export POSTGRES_PASSWORD="${SUPERADMIN_PASS}"

set -e

# start_message (manager starts really early, send_message might fail if wait_for_service is not called first, but let's try)
start_message

/usr/bin/create_local_ca.sh "${STACK}"

wait_for_service "datastore" "6379"

show_banner "Uvicorn: $(uvicorn --version)"

/usr/sbin/crond &
/usr/bin/renew_crl

# send_message ""

uvicorn main:app --host "0.0.0.0" --port 8080 --log-level info

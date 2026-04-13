#!/bin/sh
set -e

. /usr/bin/common.sh
export MIGASFREE_SECRET_DIR=/var/run/secrets

load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
BROKER_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"

set_tz
start_message

show_banner "celery $(celery --version)"

# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
{
    echo "broker_url = '${BROKER_URL}'"
    echo "result_backend = '${BROKER_URL}'"
    echo "broker_connection_retry_on_startup = True"
    echo "enable_utc = False"
    echo "timezone = '${TZ}'"
} > "${CONFIG_FILE}"

send_message ""

export FLOWER_UNAUTHENTICATED_API=True

if [ "$(id -u)" = '0' ]
then
    chown flower:flower "${CONFIG_FILE}"
    exec su flower -s /bin/sh -c "celery --config celeryconfig flower --persistent=False --max_tasks=5000 --broker-api='${BROKER_URL}/api/'"
fi

celery --config celeryconfig flower --persistent=False --max_tasks=5000 --broker-api="${BROKER_URL}/api/"

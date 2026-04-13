#!/bin/sh

. /usr/bin/common.sh
export MIGASFREE_FQDN=core:8080
export MIGASFREE_SECRET_DIR=/var/run/secrets

QUEUES="pms-apt"
load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
BROKER_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"
export CELERY_BROKER_URL="${BROKER_URL}"

# shellcheck source=/dev/null
. /venv/bin/activate

start_message
set_tz

export MIGASFREE_KEYS_DIR=/var/lib/migasfree-backend/keys
mkdir -p "$(dirname "${MIGASFREE_KEYS_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/keys" "${MIGASFREE_KEYS_DIR}"

export MIGASFREE_PUBLIC_DIR=/var/lib/migasfree-backend/public
mkdir -p "$(dirname "${MIGASFREE_PUBLIC_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/public" "${MIGASFREE_PUBLIC_DIR}"

export MIGASFREE_TMP_DIR=/var/lib/migasfree-backend/tmp
mkdir -p "$(dirname "${MIGASFREE_TMP_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/tmp" "${MIGASFREE_TMP_DIR}"

export MIGASFREE_CERTIFICATES_DIR=/var/lib/migasfree-backend/certificates
mkdir -p "$(dirname "${MIGASFREE_CERTIFICATES_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/certificates" "${MIGASFREE_CERTIFICATES_DIR}"

export MIGASFREE_STORE_TRAILING_PATH=stores
export MIGASFREE_REPOSITORY_TRAILING_PATH=repos
export MIGASFREE_EXTERNAL_TRAILING_PATH=external
export MIGASFREE_TMP_TRAILING_PATH=tmp

send_message "waiting ${MIGASFREE_FQDN%:*}"
wait_for_service "${MIGASFREE_FQDN%:*}" "${MIGASFREE_FQDN#*:}"

show_banner "celery $(celery --version)"

cd /pms || exit 1

# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
{
    echo "broker_url = '${BROKER_URL}'"
    echo "result_backend = '${BROKER_URL}'"
    echo "imports = ('migasfree.core.pms.tasks',)"
    echo "broker_connection_retry_on_startup = True"
    echo "worker_concurrency = 3"
} > "${CONFIG_FILE}"

send_message ""
celery --config celeryconfig worker -l INFO --uid=www-data -Q "$QUEUES"

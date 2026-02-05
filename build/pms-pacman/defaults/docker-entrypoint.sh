#!/bin/bash

export MIGASFREE_FQDN=core:8080
export MIGASFREE_SECRET_DIR=/var/run/secrets

QUEUES="pms-pacman"
BROKER_URL=redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0
export CELERY_BROKER_URL=${BROKER_URL}

function wait {
    local _SERVER=$1
    local _PORT=$2
    local _COUNTER=0
    until [ $_COUNTER -gt 30 ]
    do
        if nc -z "$_SERVER" "$_PORT" 2> /dev/null
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        ((_COUNTER++))
    done
    echo "Rebooting container"
    exit 1
}


. /venv/bin/activate
send_message "starting ${SERVICE:(${#STACK})+1}"

export MIGASFREE_KEYS_DIR=/var/lib/migasfree-backend/keys
mkdir -p "$(dirname ${MIGASFREE_KEYS_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/keys" ${MIGASFREE_KEYS_DIR}

export MIGASFREE_PUBLIC_DIR=/var/lib/migasfree-backend/public
mkdir -p "$(dirname ${MIGASFREE_PUBLIC_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/public" ${MIGASFREE_PUBLIC_DIR}

export MIGASFREE_TMP_DIR=/var/lib/migasfree-backend/tmp
mkdir -p "$(dirname ${MIGASFREE_TMP_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/tmp" ${MIGASFREE_TMP_DIR}

export MIGASFREE_CERTIFICATES_DIR=/var/lib/migasfree-backend/certificates
mkdir -p "$(dirname ${MIGASFREE_CERTIFICATES_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/certificates" ${MIGASFREE_CERTIFICATES_DIR}

export MIGASFREE_STORE_TRAILING_PATH=stores
export MIGASFREE_REPOSITORY_TRAILING_PATH=repos
export MIGASFREE_EXTERNAL_TRAILING_PATH=external
export MIGASFREE_TMP_TRAILING_PATH=tmp

send_message "waiting ${MIGASFREE_FQDN%:*}"
wait "${MIGASFREE_FQDN%:*}" "${MIGASFREE_FQDN#*:}"

echo "


                   █                          ██
                                             █
         ███ ██    █    ██     ███     ███  ████  ███  ███    ███
        █   █  █   █   █  █       █   █      █   █    █   █  █   █
        █   █  █   █   █  █    ████    ██    █   █    ████   ████
        █   █  █   █   █  █   █   █      █   █   █    █      █
        █   █  █   █    ███    ███    ███    █   █     ███    ███
                          █
        we love change  ██


        $SERVICE ($TAG)
        celery $(celery --version)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

cd /pms

# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
echo "broker_url = '${BROKER_URL}'" > ${CONFIG_FILE}
echo "result_backend = '${BROKER_URL}'" >> ${CONFIG_FILE}
echo "imports = ('migasfree.core.pms.tasks',)" >> ${CONFIG_FILE}
echo "broker_connection_retry_on_startup = True" >> ${CONFIG_FILE}
echo "worker_concurrency = 3" >> ${CONFIG_FILE}

send_message ""
celery --config celeryconfig worker -l INFO --uid=890 -Q $QUEUES

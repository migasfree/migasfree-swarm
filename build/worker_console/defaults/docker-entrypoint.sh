#!/bin/sh

export MIGASFREE_SECRET_DIR=/var/run/secrets
BROKER_URL=redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0

set_TZ() {
    : ${TZ:=Europe/Madrid}
    # Link only if the target differs (reduces noisy “File exists” errors)
    [ "$(readlink /etc/localtime)" != "/usr/share/zoneinfo/$TZ" ] && \
        ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime
}

wait() {
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

send_message "init worker console"
# send_message "wait worker"
# wait worker 8080

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
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
echo "broker_url = '${BROKER_URL}'" > ${CONFIG_FILE}
echo "result_backend = '${BROKER_URL}'" >> ${CONFIG_FILE}
echo "broker_connection_retry_on_startup = True" >> ${CONFIG_FILE}
echo "enable_utc = False" >> ${CONFIG_FILE}
echo "timezone = '${TZ}'" >> ${CONFIG_FILE}

send_message ""

export FLOWER_UNAUTHENTICATED_API=True
celery --config celeryconfig flower --persistent=False --max_tasks=5000 --broker-api="${BROKER_URL}/api/"

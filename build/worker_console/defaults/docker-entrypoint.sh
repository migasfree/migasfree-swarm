#!/bin/sh
set -e

export MIGASFREE_SECRET_DIR=/var/run/secrets
BROKER_URL="redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0"

set_TZ() {
    TZ="${TZ:-Europe/Madrid}"
    # Link only if the target differs (reduces noisy “File exists” errors)
    if [ "$(readlink /etc/localtime)" != "/usr/share/zoneinfo/$TZ" ]
    then
        ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    fi
}

wait() {
    _SERVER=$1
    _PORT=$2
    _COUNTER=0
    until [ "$_COUNTER" -gt 30 ]
    do
        if nc -z "$_SERVER" "$_PORT" 2> /dev/null
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        _COUNTER=$((_COUNTER + 1))
    done
    echo "Rebooting container"
    exit 1
}

set_TZ
_SERVICE_NAME=${SERVICE#${STACK}_}
send_message "starting $_SERVICE_NAME"

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
        Container: $(hostname)
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

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

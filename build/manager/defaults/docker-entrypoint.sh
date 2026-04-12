#!/bin/sh

# Set Timezone
if [ -n "$TZ" ] && [ -f "/usr/share/zoneinfo/$TZ" ]; then
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "$TZ" > /etc/timezone
fi

MIGASFREE_SECRET_DIR='/var/run/secrets'
REDIS_URL="redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0"
export REDIS_URL
POSTGRES_PASSWORD=$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")
export POSTGRES_PASSWORD

set -e

wait_for_service() {
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

# send_message "Starting Certificate Authority"

/usr/bin/create_local_ca.sh "${STACK}"

wait_for_service "datastore" "6379"

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
        Uvicorn: $(uvicorn --version)
        Container: $(hostname)
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

/usr/sbin/crond &
/usr/bin/renew_crl

# send_message ""

uvicorn main:app --host "0.0.0.0" --port 8080 --log-level info

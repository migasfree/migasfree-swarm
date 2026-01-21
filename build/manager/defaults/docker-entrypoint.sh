#!/bin/sh

MIGASFREE_SECRET_DIR='/var/run/secrets'
export REDIS_URL=redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0
export POSTGRES_PASSWORD=$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")

set -e

wait_for_service() {
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

# send_message "Starting Certificate Authority"

/usr/bin/create_local_ca.sh ${STACK}

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
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

/usr/sbin/crond &
/usr/bin/renew_crl

# send_message ""

uvicorn main:app --host "0.0.0.0" --port 8080 --log-level info

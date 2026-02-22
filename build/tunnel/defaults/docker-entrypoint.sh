#!/bin/sh

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


send_message "waiting datastore"
wait_for_service "datastore" "6379"

send_message "Starting Tunnelnode"


MIGASFREE_SECRET_DIR='/var/run/secrets'
export REDIS_URL=redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0




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
        $(python --version)
        Container: $HOSTNAME
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

send_message ""

exec python3 -u main.py
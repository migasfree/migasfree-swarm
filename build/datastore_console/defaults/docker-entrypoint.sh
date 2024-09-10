#!/bin/sh
set -e

MIGASFREE_SECRET_DIR=/var/run/secrets

function wait {
    local _SERVER=$1
    local _PORT=$2
    local _COUNTER=0

    until [ $_COUNTER -gt 30 ]
    do
        nc -z $_SERVER $_PORT 2> /dev/null
        if [ $? -eq 0 ]
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        _COUNTER=$(( $_COUNTER + 1 ))
    done
    echo "Rebooting container"
    exit 1
}

function set_TZ {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime || :
}

send_message "starting ${SERVICE:(${#STACK})+1}"

set_TZ


send_message "waiting datastore"
wait $REDIS_HOST $REDIS_PORT


send_message "init datashare"

echo "


                   ●                          ●●
                                             ●
         ●●● ●●    ●    ●●     ●●●     ●●●  ●●●●  ●●●  ●●●    ●●●
        ●   ●  ●   ●   ●  ●       ●   ●      ●   ●    ●   ●  ●   ●
        ●   ●  ●   ●   ●  ●    ●●●●    ●●    ●   ●    ●●●●   ●●●●
        ●   ●  ●   ●   ●  ●   ●   ●      ●   ●   ●    ●      ●
        ●   ●  ●   ●    ●●●    ●●●    ●●●    ●   ●     ●●●    ●●●
                          ●
                        ●●

        $SERVICE ($TAG)
        redisinsight
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"




send_message ""
reload_proxy

su node -c "/usr/bin/add_connection" &
su node -c "cd /usr/src/app;node redisinsight/api/dist/src/main"

#!/bin/sh
set -e

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

set_TZ() {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs "/usr/share/zoneinfo/$TZ" /etc/localtime || :
}

_SERVICE_NAME=${SERVICE#${STACK}_}
send_message "starting $_SERVICE_NAME"

set_TZ

send_message "waiting datastore"
wait "$REDIS_HOST" "$REDIS_PORT"

send_message "init datashare"

REDISINSIGHT_VERSION=$(sed -n 's/.*"version": "\([^"]*\)".*/\1/p' /usr/src/app/redisinsight/api/dist/package.json)
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
        redisinsight $REDISINSIGHT_VERSION
        Container: $(hostname)
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

send_message ""

su node -c "/usr/bin/add_connection" &
su node -c "cd /usr/src/app; node redisinsight/api/dist/src/main"

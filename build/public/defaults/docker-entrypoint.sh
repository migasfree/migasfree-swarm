#!/bin/sh
set -e

set_TZ() {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime || :
}

wait_for_service() {
    _SERVER=$1
    _PORT=$2
    _COUNTER=0

    until [ "$_COUNTER" -gt 60 ]
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

_SERVICE_NAME=${SERVICE#${STACK}_}
send_message "starting $_SERVICE_NAME"

set_TZ

export MIGASFREE_CONF_DIR=/var/lib/migasfree-backend/conf
mkdir -p "$(dirname "${MIGASFREE_CONF_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/conf" "${MIGASFREE_CONF_DIR}"

export MIGASFREE_PUBLIC_DIR=/var/migasfree/public
mkdir -p "$(dirname "${MIGASFREE_PUBLIC_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/public" "${MIGASFREE_PUBLIC_DIR}"

export MIGASFREE_POOL_DIR=/var/migasfree/pool
mkdir -p "$(dirname "${MIGASFREE_POOL_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/pool" "${MIGASFREE_POOL_DIR}"

_CONTAINER=$(hostname)
sed -i "s/@container@/$_CONTAINER/g" /var/migasfree/404.html
sed -i "s/@container@/$_CONTAINER/g" /var/migasfree/50x.html

# TODO: Remove link. Warning!!! Afect to symbolic links of packages in REPOSITORIES.
# ¿Changes MIGASFREE_PUBLIC_DIR = '/var/migasfree/repo' in source?
ln -snf /var/migasfree/public /var/migasfree/repo

send_message "waiting core"
wait_for_service core 8080

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
        $(nginx -v 2>&1)
        Container: $(hostname)
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

# Reload extensions for haproxy.cfg (even if named haproxy, it seems to be used here)
# ======================================
/usr/bin/update_extensions.sh

# Get external deployments extensions from manager
# ================================================
curl -s http://manager:8080/manager/v1/private/nginx_extensions > /var/tmp/external-deployments.conf || :

send_message ""

exec nginx -g 'daemon off;'

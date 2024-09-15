#!/bin/sh
set -e

export MIGASFREE_SECRET_DIR=/var/run/secrets

function set_TZ {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime || :
}


function cron_init
{
    if [ -z "$BACKUP_CRON" ]; then
        BACKUP_CRON="0 0 * * *"
    fi
    CRON=$(echo "$BACKUP_CRON" |tr -d "'") # remove single quote
    echo "$CRON /usr/bin/backup" > /tmp/cron
    crontab /tmp/cron
    rm /tmp/cron

    crond -l 2 -f > /dev/stdout 2> /dev/stderr &
}

send_message "starting ${SERVICE:(${#STACK})+1}"

set_TZ
cron_init

# first arg is `-f` or `--some-option`
# or first arg is `something.conf`
if [ "${1#-}" != "$1" ] || [ "${1%.conf}" != "$1" ]
then
    set -- redis-server "$@"
fi

# allow the container to be started with `--user`
if [ "$1" = 'redis-server' -a "$(id -u)" = '0' ]
then
    find . \! -user redis -exec chown redis '{}' +
    exec su-exec redis "$0" "$@"
fi


send_message ""
reload_proxy 3

redis-server --requirepass $(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass) --protected-mode yes  --appendonly yes


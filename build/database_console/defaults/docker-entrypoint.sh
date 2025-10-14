#!/bin/sh
set -e

MIGASFREE_SECRET_DIR=/var/run/secrets

export PGADMIN_DEFAULT_EMAIL="$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_name)@${FQDN}"

wait_for_dns "proxy"

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


chown pgadmin:root /run/pgadmin
chown pgadmin:root /pgadmin4/config_distro.py

send_message "init database_console"

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
        pgadmin4
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"



send_message ""

# Changes to USER pgadmin
if [ "$(id -u)" = '0' ]; then
    exec su-exec pgadmin "$0" "$@"
fi

/usr/bin/add_connection &
/entrypoint.sh

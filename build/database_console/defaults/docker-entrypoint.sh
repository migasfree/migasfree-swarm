#!/bin/sh
set -e

MIGASFREE_SECRET_DIR=/var/run/secrets


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
        pgadmin4
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"



send_message ""
reload_proxy

# Changes to USER pgadmin
if [ "$(id -u)" = '0' ]; then
    exec su-exec pgadmin "$0" "$@"
fi

/usr/bin/add_connection &
/entrypoint.sh

#!/bin/bash

set -e

function capture_message {
    local _LAST="database system is ready to accept connections"

    if [[ "$1" == *"$_LAST"* ]]
    then
        send_message ""
    else
        send_message "$1"
    fi
}

function set_TZ {
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


if nc -z database 5432 >/dev/null
then
   echo "WARNING: Only one database replica is allowed."
   exit 1
fi


# Changes UID and GID for backup and restore in datashare
OWNER_UID=890
OWNER_GID=890
sed -e "/^postgres/s=^postgres:x:[0-9]*:[0-9]*:=postgres:x:${OWNER_UID}:${OWNER_GID}:=" -i /etc/passwd
sed -e "/^postgres/s=^postgres:x:[0-9]*:=postgres:x:${OWNER_GID}:=" -i /etc/group


send_message "starting ${SERVICE:(${#STACK})+1}"
#set_TZ
cron_init

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
        $(postgres -V)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"




send_message ""
reload_proxy

# if no database dump exists, one will be created.
if ! [ -f ${DATASHARE_MOUNT_PATH}/dump/migasfree.sql ]
then
    sh -c "sleep 60;backup" &
fi

# Run docker-entrypoint.sh (from postgres image)
/usr/local/bin/docker-entrypoint.sh postgres

# Capture stdout line by line
#stdbuf -oL bash /usr/local/bin/docker-entrypoint.sh postgres |
#    while IFS= read -r _LINE
#    do
#        capture_message "$_LINE"
#    done

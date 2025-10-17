#!/bin/sh

pg_isready -d "${POSTGRES_DB}" -U "${POSTGRES_USER}"
if [ $? -eq 0 ]
then
    if ! [ -f /var/tmp/healthy ]
    then
        touch /var/tmp/healthy
        send_message ""
    fi
    exit 0
else
    rm /var/tmp/healthy || :
    send_message "Unavailable"
    exit 1
fi
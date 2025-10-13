#!/bin/sh

timeout 1 curl --fail --silent --head --request GET http://localhost:${PGADMIN_LISTEN_PORT}/misc/ping > /dev/null
if [ $? -eq 0 ]
then
    if ! [ -f /var/tmp/healthy ]
    then
        touch /var/tmp/healthy
        send_message ""
    fi
else
    rm /var/tmp/healthy || :
    send_message "Service Unavailable"
    exit 1
fi

exit 0
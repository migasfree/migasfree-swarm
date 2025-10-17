#!/bin/sh

timeout 1 curl --fail --silent --head --request GET http://127.0.0.1:80/ > /dev/null
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
#!/bin/sh

timeout 1 redis-cli ping > /dev/null
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
    send_message "Service Unavailable"
    exit 1
fi
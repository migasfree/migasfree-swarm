#!/bin/sh

if curl -f http://127.0.0.1:8080
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
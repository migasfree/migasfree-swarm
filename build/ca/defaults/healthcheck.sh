#!/bin/sh

if curl -f http://127.0.0.1:80/ca/health
then
    if ! [ -f /var/tmp/healthy ]
    then
        touch /var/tmp/healthy
    fi
    exit 0
else
    rm /var/tmp/healthy || :
    exit 1
fi

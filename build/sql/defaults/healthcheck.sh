#!/bin/sh
timeout 1 curl --fail --silent --head --request GET http://127.0.0.1:8080/health > /dev/null
if [ $? -eq 0 ]
then
    if ! [ -f /var/tmp/healthy ]
    then
        touch /var/tmp/healthy
        # Important: Reconfigure in the background after 3 seconds; this container must be healthy first.
        reload_proxy 3

    fi
else
    rm /var/tmp/healthy || :
    exit 1
fi

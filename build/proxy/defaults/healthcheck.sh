#!/bin/sh

timeout 1 curl --fail --silent --head --request GET http://127.0.0.1:8001/services/status > /dev/null
if [ $? -eq 0 ]
then
    if ! [ -f /var/tmp/healthy ]
    then
        touch /var/tmp/healthy
    fi
else
    rm /var/tmp/healthy || :
    exit 1  
fi


#!/bin/sh

_ROOT="/srv"

PORT=${FB_PORT:-$(jq .port /.filebrowser.json)}
timeout 1 curl --fail --silent --head --request GET http://localhost:$PORT/health > /dev/null
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


timeout 1 ls ${_ROOT}/conf/ >/dev/null
if ! [ $? -eq 0 ]
then
    rm /var/tmp/healthy || :
    send_message "File system disconnected"
    echo "$(date) File system disconnected"
    exit 1
fi

exit 0
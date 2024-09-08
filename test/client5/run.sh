#!/bin/bash

source ../../config/env/general
source ../../config/env/stack

if [ "$HTTPSMODE" = "manual" ]
then
#    cp /exports/migasfree/certificates/ca.crt defaults/usr/share/ca-certificates/ca.crt
    cp /home/alberto/Descargas/ca.crt defaults/usr/share/ca-certificates/ca.crt
fi

docker build . -t migasfree/client:5.0-beta
docker run --rm \
    -e TZ="Europe/Madrid" \
    -e MIGASFREE_CLIENT_SERVER=${FQDN} \
    -e MIGASFREE_CLIENT_PROJECT=acme \
    -e MIGASFREE_CLIENT_PROTOCOL=https \
    -e MIGASFREE_CLIENT_PORT= \
    -e USER=root \
    -ti migasfree/client:5.0 bash

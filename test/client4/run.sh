#!/bin/bash

source ../../config/env/general
source ../../config/env/stack

if [ "$HTTPSMODE" = "manual" ]
then
    cp /exports/migasfree/certificates/ca.crt defaults/usr/share/ca-certificates/ca.crt
fi

docker build . -t migasfree/client:4.20
docker run --rm \
    -e TZ="Europe/Madrid" \
    -e MIGASFREE_CLIENT_SERVER=${FQDN}:443 \
    -e MIGASFREE_CLIENT_PROJECT=acme \
    -e MIGASFREE_CLIENT_PROTOCOL=https \
    -e MIGASFREE_CLIENT_PORT= \
    -e USER=root \
    -ti migasfree/client:4.20 bash

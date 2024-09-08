#!/bin/bash

source ../../config/env/general
source ../../config/env/stack

if [ "$HTTPSMODE" = "manual" ]
then
    cp /exports/migasfree/certificates/ca.crt defaults/usr/share/ca-certificates/ca.crt
fi

docker build . -t migasfree/client-arch:5.0-beta
docker run --rm \
    -e TZ="Europe/Madrid" \
    -e MIGASFREE_CLIENT_SERVER=${FQDN} \
    -e MIGASFREE_CLIENT_PROJECT=ARCH \
    -e MIGASFREE_CLIENT_PROTOCOL=https \
    -e MIGASFREE_CLIENT_PORT= \
    -e MIGASFREE_CLIENT_DEBUG=True \
    -e USER=root \
    -ti migasfree/client-arch:5.0-beta bash

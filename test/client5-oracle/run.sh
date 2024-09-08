#!/bin/bash

source ../../config/env/general
source ../../config/env/stack

if [ "$HTTPSMODE" = "manual" ]
then
    cp /exports/migasfree/certificates/ca.crt defaults/usr/share/ca-certificates/ca.crt
    # cert must be in PEM format
    openssl x509 -in defaults/usr/share/ca-certificates/ca.crt -out defaults/usr/share/ca-certificates/ca.pem -outform PEM
fi

docker build . -t migasfree/client-oracle:5.0-beta
docker run --rm \
    -e TZ="Europe/Madrid" \
    -e MIGASFREE_CLIENT_SERVER=${FQDN} \
    -e MIGASFREE_CLIENT_PROJECT=fedora \
    -e MIGASFREE_CLIENT_PROTOCOL=https \
    -e MIGASFREE_CLIENT_PORT= \
    -e USER=root \
    -ti migasfree/client-oracle:5.0-beta bash

#!/bin/bash

source ../../config/env/general
source ../../config/env/stack

if [ "$HTTPSMODE" = "manual" ]
then
    cp /exports/migasfree/certificates/ca.crt defaults/usr/share/ca-certificates/ca.crt
fi

docker build . -t migasfree/winget:5.0-beta
docker run --rm -ti -v "/exports/migasfree/keys:/keys" -v "/exports/migasfree/certificates:/certificates"  -v "/exports/migasfree/public:/public" migasfree/winget:-beta bash 

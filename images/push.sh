#!/bin/bash
VERSION=$(cat ../VERSION)

# Need login
# docker login

_IMAGES="$1"
if [ -z "${_IMAGES}" ]
then
    _IMAGES="swarm proxy certbot datashare_console datastore datastore_console database database_console sql core console public worker_console pms-apt pms-yum pms-pacman pms-wpt"
fi

for _IMAGE in ${_IMAGES}
do
    docker push migasfree/${_IMAGE}:${VERSION}
done
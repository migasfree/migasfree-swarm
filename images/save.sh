#!/bin/bash

_VERSION=$(cat ../VERSION)

_IMAGES="$1"
if [ -z "${_IMAGES}" ]
then
    _IMAGES="swarm proxy ca certbot datashare_console datastore datastore_console database database_console assistant mcp-server core console public worker_console pms-apt pms-yum pms-pacman pms-wpt"
fi

for _IMAGE in ${_IMAGES}
do
    docker save --output "./migasfree-${_IMAGE}-${_VERSION}.tar" "migasfree/${_IMAGE}:${_VERSION}"
done

#!/bin/bash

_VERSION=$(cat ../VERSION)

_IMAGES="$1"
if [ -z "${_IMAGES}" ]
then
    _IMAGES="swarm proxy manager certbot datashare_console datastore datastore_console pgpool database database_console mcp-server core console public worker_console tunnel pms-apt pms-yum pms-pacman pms-wpt"
fi

for _IMAGE in ${_IMAGES}
do
    docker save --output "./migasfree-${_IMAGE}-${_VERSION}.tar" "migasfree/${_IMAGE}:${_VERSION}"
done

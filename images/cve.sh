#!/bin/bash

# https://github.com/aquasecurity/trivy
# apt install trivy

_IMAGES="$1"
if [ -z "${_IMAGES}" ]
then
    trivy clean --all
    _IMAGES="swarm proxy certbot datashare_console datastore datastore_console database database_console assistant mcp-server core console public worker_console pms-apt pms-yum pms-pacman pms-wpt"
fi

for _IMAGE in ${_IMAGES}
do
    trivy image migasfree/${_IMAGE}:$(cat ../VERSION) > ${_IMAGE}.log
done
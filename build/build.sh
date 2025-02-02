#!/bin/bash

function build
{
    local _CONTEXT="$1"
    if [ -d ./$_CONTEXT ]
    then
        mkdir -p $_CONTEXT/defaults/usr/bin/
        cp scripts/* $_CONTEXT/defaults/usr/bin/

        pushd "$_CONTEXT" > /dev/null
        local _TAG=$(cat ../../VERSION)
        echo -n "${_TAG}" > ./VERSION
        echo
        echo
        echo "BUILD: ${_CONTEXT}:${_TAG}"
        echo "============================================================================"
        docker --debug build . --build-arg TAG=${_TAG} -t "migasfree/${_CONTEXT}:${_TAG}"
        popd > /dev/null
    fi
}

_IMAGES="$1"
if [ -z "${_IMAGES}" ]
then
    _IMAGES="swarm proxy certbot datashare_console datastore datastore_console database database_console assistant core console public worker_console pms-apt pms-yum pms-pacman pms-wpt"
fi

for _IMAGE in ${_IMAGES}
do
    build "${_IMAGE}"
done

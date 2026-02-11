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
        docker --debug build ${_NO_CACHE} . --build-arg TAG=${_TAG} -t "migasfree/${_CONTEXT}:${_TAG}"
        popd > /dev/null
    fi
}

DEFAULT_IMAGES="swarm manager proxy certbot datashare_console datastore datastore_console database database_console mcp-server core console public worker_console tunnel pms-apt pms-yum pms-pacman pms-wpt pms-apk"

function usage
{
    echo "Usage: $0 [options] [image1 image2 ...]"
    echo
    echo "Options:"
    echo "  --no-cache      Do not use cache when building the image"
    echo "  --list, -l      List available images"
    echo "  --help, -h      Show this help message"
    echo
    echo "If no images are specified, all default images will be built."
}

_NO_CACHE=""
_IMAGES=""

for arg in "$@"
do
    case $arg in
        --no-cache)
        _NO_CACHE="--no-cache"
        ;;
        --help|-h)
        usage
        exit 0
        ;;
        --list|-l)
        echo "Available images:"
        for img in $DEFAULT_IMAGES; do
            echo "  - $img"
        done
        exit 0
        ;;
        *)
        _IMAGES="${_IMAGES} $arg"
        ;;
    esac
done

if [ -z "${_IMAGES}" ]
then
    _IMAGES="$DEFAULT_IMAGES"
fi

for _IMAGE in ${_IMAGES}
do
    build "${_IMAGE}"
done

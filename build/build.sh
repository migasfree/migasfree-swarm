#!/bin/bash

function build
{
    local _CONTEXT="$1"
    if [ -d "./$_CONTEXT" ]
    then
        mkdir -p "$_CONTEXT/defaults/usr/bin/"
        cp scripts/* "$_CONTEXT/defaults/usr/bin/"
        chmod +x "$_CONTEXT/defaults/usr/bin/"*

        pushd "$_CONTEXT" > /dev/null || return 1
        local _TAG
        _TAG=$(cat ../../VERSION)
        echo -n "${_TAG}" > ./VERSION
        echo
        echo
        echo "BUILD: ${_CONTEXT}:${_TAG}"
        echo "============================================================================"
        docker --debug build ${_NO_CACHE} . --build-arg "TAG=${_TAG}" -t "migasfree/${_CONTEXT}:${_TAG}"
        _RET=$?
        popd > /dev/null || return 1
        return $_RET
    fi
}

DEFAULT_IMAGES="swarm manager proxy certbot datashare_console datastore datastore_console  pgpool database database_console mcp-server core console public worker_console tunnel pms-apt pms-yum pms-pacman pms-wpt pms-apk"

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
            for img in $DEFAULT_IMAGES
            do
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

SUCCESS_COUNT=0
FAILURE_COUNT=0
SUCCESS_IMAGES=""
FAILURE_IMAGES=""

for _IMAGE in ${_IMAGES}
do
    if build "${_IMAGE}"
    then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        SUCCESS_IMAGES="${SUCCESS_IMAGES} ${_IMAGE}"
    else
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        FAILURE_IMAGES="${FAILURE_IMAGES} ${_IMAGE}"
    fi
done

echo
echo "============================================================================"
echo "BUILD SUMMARY"
echo "============================================================================"
echo "Total images: $((SUCCESS_COUNT + FAILURE_COUNT))"
echo "Success:      ${SUCCESS_COUNT}"
echo "Failure:      ${FAILURE_COUNT}"

if [ "${FAILURE_COUNT}" -gt 0 ]
then
    echo
    echo "FAILED IMAGES:"
    for img in ${FAILURE_IMAGES}
    do
        echo "  - ${img}"
    done
    exit 1
fi

echo
echo "All images built successfully!"
exit 0

#!/bin/sh
set -e

VERSION=$(cat /VERSION)

# migasfree images
for _IMG in swarm proxy certbot datashare_console datastore datastore_console database database_console core console public worker_console tunnel mcp-server pms-apt pms-yum pms-pacman pms-apk pms-wpt
do
    _IMAGE="migasfree/${_IMG}:${VERSION}"
    if docker image inspect "${_IMAGE}" > /dev/null 2>&1
    then
        echo "Image ${_IMAGE} already exists locally."
    else
        docker pull "${_IMAGE}"
    fi
done

# portainer images
# Extract images from portainer.template securely
_PORTAINER_IMAGES=$(grep "image:" /tools/templates/portainer.template | awk '{print $2}')

for _IMG in $_PORTAINER_IMAGES
do
    if [ -n "$_IMG" ]; then
        if docker image inspect "$_IMG" > /dev/null 2>&1; then
            echo "Image $_IMG already exists locally."
        else
            docker pull "$_IMG"
        fi
    fi
done

#!/bin/sh
VERSION=$(cat /VERSION)

# migasfree images
for _IMG in swarm proxy certbot datashare_console datastore datastore_console database database_console assistant core console public worker_console pms-apt pms-yum pms-pacman pms-wpt
do
    _IMAGE="migasfree/${_IMG}:${VERSION}"
    if docker image inspect "${_IMAGE}" > /dev/null 2>&1; then
        echo "Image ${_IMAGE} already exists locally."
    else
        docker pull "${_IMAGE}"
    fi


done

# portainer images
for _IMG in $(grep "image:" /tools/templates/portainer.template | awk  '{print $2}')
do
    if docker image inspect "$_IMG" > /dev/null 2>&1; then
        echo "Image $_IMG already exists locally."
    else
        docker pull "$_IMG"
    fi
done
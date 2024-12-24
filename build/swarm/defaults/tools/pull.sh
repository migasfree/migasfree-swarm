#!/bin/sh
VERSION=$(cat /VERSION)

# migasfree images
for _IMG in swarm proxy certbot datashare_console datastore datastore_console database database_console assistant core console public worker_console pms-apt pms-yum pms-pacman pms-wpt
do
    docker pull migasfree/${_IMG}:${VERSION}
done

# portainer images
for _IMG in $(grep "image:" /tools/templates/portainer.template | awk  '{print $2}')
do
    docker pull $_IMG
done
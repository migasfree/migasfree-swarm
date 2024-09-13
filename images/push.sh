#!/bin/bash
VERSION=$(cat ../VERSION)

# Need login
# docker login

for _IMG in swarm proxy public datashare datashare_console database database_console datastore datastore_console worker_console client certbot pms-apt pms-yum pms-winget pms-pacman pms-wpt
do
    docker push migasfree/${_IMG}:${VERSION}
done
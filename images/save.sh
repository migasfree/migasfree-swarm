#!/bin/bash

_VERSION=$(cat ../VERSION)
for _IMG in swarm proxy certbot datashare_console datastore datastore_console database database_console core console public worker_console pms-apt pms-yum pms-pacman pms-winget pms-wpt
do
    docker save --output ./migasfree-${_IMG}-${_VERSION}.tar migasfree/${_IMG}:${_VERSION}
done


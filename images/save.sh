#!/bin/bash

_VERSION=$(cat ../VERSION)
for _IMG in swarm proxy public datashare datashare_console database database_console datastore datastore_console worker_console client certbot pms-apt pms-yum pms-winget pms-pacman pms-wpt
do
    docker save --output ./migasfree-${_IMG}-${_VERSION}.tar migasfree/${_IMG}:${_VERSION}
done

_VERSION=master
for _IMG in console core
do
    docker save --output ./migasfree-${_IMG}-${_VERSION}.tar migasfree/${_IMG}:${_VERSION}
done

_VERSION=4.20
for _IMG in client
do
    docker save --output ./migasfree-${_IMG}-${_VERSION}.tar migasfree/${_IMG}:${_VERSION}
done

chmod -R 644 ./*.tar

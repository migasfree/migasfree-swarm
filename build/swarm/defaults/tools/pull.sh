#!/bin/sh
VERSION=$(cat /VERSION)

for _IMG in proxy public console datashare_console database database_console datastore datastore_console core worker_console certbot pms-apt pms-yum
do
    docker pull migasfree/${_IMG}:${VERSION}
done
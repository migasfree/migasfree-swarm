#!/bin/bash
VERSION=$(cat ../VERSION)

# Need login
# docker login

for _IMG in swarm proxy public console datashare_console database database_console datastore datastore_console core worker_console certbot pms-apt pms-yum
do
    docker push migasfree/${_IMG}:${VERSION}
done
#!/bin/sh

VERSION=$(cat /VERSION)

. /stack/env.py


if [ "${DATASHARE_FS}" = 'nfs' ]
then
    echo
    echo
    echo "==================================================================================================================="
    echo
    echo "Before adding a worker node to the cluster, ensure the following on the machine that will serve as the worker node:"
    echo
    echo "  1. 'Docker Engine' is installed ( https://docs.docker.com/engine/install/ )"
    echo
    echo "  2. The 'nfs-common' package is installed"
    echo
    echo
    echo "Once these prerequisites are met:"
    echo ""
    echo "  3. To create the migasfree-swarm volume:"
    echo
    echo "    docker volume create --driver local --opt type=nfs \\"
    echo "        --opt o=addr=${DATASHARE_SERVER},port=${DATASHARE_PORT},rw,vers=4 \\"
    echo "        --opt device=:${DATASHARE_PATH} migasfree-swarm"
    echo
    echo "  4. Pull images:"
    echo
    echo "    docker run --detach=false --rm -ti \\"
    echo "         -v /var/run/docker.sock:/var/run/docker.sock \\"
    echo "         migasfree/swarm:${VERSION} pull"
    echo
    echo -n "  5.$(docker swarm join-token worker)"
    echo
    echo
    echo "==================================================================================================================="
    echo


else

    echo
    echo
    echo "When DATASHARE_FS is set to '$DATASHARE_FS', you cannot add a node to the cluster."

    read -p "Do you want to switch to NFS mode? (y/n): " response
    response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
    if [[ "$response" == "y" || "$response" == "yes" ]]; then
            echo "DATASHARE_FS='nfs'" > /stack/env.py
            python3 /tools/config.py
    fi

fi

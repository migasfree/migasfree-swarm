#!/bin/sh

CONTAINER_PROXY_ID=$(docker ps|grep infra_proxy| awk '{print $1}')
echo
echo "● proxy & portainer:"
echo
docker exec -ti ${CONTAINER_PROXY_ID} sh -c "echo -n '    ';cat /var/run/secrets/swarm-credential | tr ':' ' ';echo"
echo

for STACK in $(ls /mnt/cluster/datashares)
do
    source /mnt/cluster/datashares/${STACK}/env.py
    echo "● Stack ${STACK}:"
    echo
    echo "    ● database_console & assistant:"
    echo
    docker exec -ti "${CONTAINER_PROXY_ID}" sh -c "echo -n '        '; cat /var/run/secrets/${STACK}_superadmin_name; echo -n @${FQDN} ;echo -n ' '; cat /var/run/secrets/${STACK}_superadmin_pass; echo"

    echo
    echo "    ● Others:"
    echo
    docker exec -ti "${CONTAINER_PROXY_ID}" sh -c "echo -n '        '; cat /var/run/secrets/${STACK}_superadmin_name; echo -n ' '; cat /var/run/secrets/${STACK}_superadmin_pass; echo"
    echo
done

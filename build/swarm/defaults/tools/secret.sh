#!/bin/sh

CONTAINER_PROXY_ID=$(docker ps|grep proxy| awk '{print $1}')
echo
echo "proxy & portainer:"
echo
docker exec -ti ${CONTAINER_PROXY_ID} sh -c "echo -n '    ';cat /var/run/secrets/swarm-credential;echo"
echo 

for STACK in $(ls /mnt/cluster/datashares)
do
    echo "Stack ${STACK}:"
    echo
    docker exec -ti "${CONTAINER_PROXY_ID}" sh -c "echo -n '    '; cat /var/run/secrets/${STACK}_superadmin_name; echo -n ':'; cat /var/run/secrets/${STACK}_superadmin_pass; echo"
    echo
done

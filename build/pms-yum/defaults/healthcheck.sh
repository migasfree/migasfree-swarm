#!/bin/sh

MIGASFREE_SECRET_DIR=/var/run/secrets
BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0

. /venv/bin/activate
cd /pms
timeout 1 celery -b ${BROKER_URL} inspect ping -d celery@${HOSTNAME} > /dev/null
if [ $? -eq 0 ]
then
    if ! [ -f /var/tmp/healthy ]
    then
        touch /var/tmp/healthy
        send_message ""
        # Important: Reconfigure in the background after 3 seconds; this container must be healthy first.
        reload_proxy 3
    fi 
else
    rm /var/tmp/healthy || :
    send_message "Unavailable"
    exit 1
fi

timeout 1 ls ${DATASHARE_MOUNT_PATH}/conf/ >/dev/null
if ! [ $? -eq 0 ]
then
    rm /var/tmp/healthy || :
    send_message "File system disconnected"
    exit 1
fi

exit 0 
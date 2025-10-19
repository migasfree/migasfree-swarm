#!/bin/sh

MIGASFREE_SECRET_DIR=/var/run/secrets
BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0

. /venv/bin/activate

cd /pms

timeout 1 ls ${DATASHARE_MOUNT_PATH}/conf/ >/dev/null
if [ $? -eq 0 ]
then
    timeout 1 celery -b ${BROKER_URL} inspect ping -d celery@${HOSTNAME} > /dev/null
else
    echo "File system disconnected"
    exit 1
fi


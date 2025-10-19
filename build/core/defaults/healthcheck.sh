#!/bin/sh

if [ "$SERVICE" = "${STACK}_core" ]
then

    # core
    curl -f http://127.0.0.1:8080

elif [ "$SERVICE" = "${STACK}_worker" ]
then

    # worker
    MIGASFREE_SECRET_DIR=/var/run/secrets
    BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0
    . /venv/bin/activate
    timeout 1 celery -b ${BROKER_URL} inspect ping -d celery@${HOSTNAME} > /dev/null

else

    # beat
    ps -p $(cat /var/tmp/celery.pid)

fi

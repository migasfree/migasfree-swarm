#!/bin/sh
set -e

if [ "$SERVICE" = "${STACK}_core" ]
then
    # core
    curl -f http://127.0.0.1:8080 > /dev/null 2>&1
elif [ "$SERVICE" = "${STACK}_worker" ]
then
    # worker
    MIGASFREE_SECRET_DIR=/var/run/secrets
    BROKER_URL="redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0"
    # shellcheck source=/dev/null
    . /venv/bin/activate
    timeout 1 celery -b "${BROKER_URL}" inspect ping -d "celery@$(hostname)" > /dev/null
else
    # beat
    if [ -f /var/tmp/celery.pid ]; then
        ps -p "$(cat /var/tmp/celery.pid)" > /dev/null 2>&1
    else
        exit 1
    fi
fi

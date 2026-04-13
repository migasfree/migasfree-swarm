#!/bin/sh
. /usr/bin/common.sh

if [ "$SERVICE" = "${STACK}_core" ]
then
    # core
    check_http http://127.0.0.1:8080
elif [ "$SERVICE" = "${STACK}_worker" ]
then
    # worker
    load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
    BROKER_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"
    check_celery_worker "${BROKER_URL}"
else
    # beat
    if [ -f /var/tmp/celery.pid ]; then
        ps -p "$(cat /var/tmp/celery.pid)" > /dev/null 2>&1
    else
        exit 1
    fi
fi

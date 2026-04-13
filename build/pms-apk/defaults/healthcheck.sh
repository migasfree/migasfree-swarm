#!/bin/sh
. /usr/bin/common.sh
load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
BROKER_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"

if ! timeout 1 ls "${DATASHARE_MOUNT_PATH}/conf/" >/dev/null
then
    echo "File system disconnected"
    exit 1
fi

check_celery_worker "${BROKER_URL}"

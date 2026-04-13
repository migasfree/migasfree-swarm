#!/bin/sh
set -e

. /usr/bin/common.sh
export MIGASFREE_SECRET_DIR=/var/run/secrets

load_secret "${STACK}_superadmin_name" "SUPERADMIN_NAME"
PGADMIN_DEFAULT_EMAIL="${SUPERADMIN_NAME}@${FQDN}"
export PGADMIN_DEFAULT_EMAIL

# Changes to USER pgadmin
if [ "$(id -u)" = '0' ]
then
    set_tz
    chown pgadmin:root /run/pgadmin
    chown pgadmin:root /pgadmin4/config_distro.py
    mkdir -p /var/lib/pgadmin ||  :
    chown pgadmin:root /var/lib/pgadmin
    exec su-exec pgadmin "$0" "$@"
fi

show_banner "pgadmin4 $(/venv/bin/python3 -c 'import version;print(version.APP_VERSION)')"

send_message ""

/usr/bin/add_connection &
/entrypoint.sh

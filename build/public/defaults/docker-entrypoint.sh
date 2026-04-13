#!/bin/sh
set -e

. /usr/bin/common.sh

start_message
set_tz

export MIGASFREE_CONF_DIR=/var/lib/migasfree-backend/conf
mkdir -p "$(dirname "${MIGASFREE_CONF_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/conf" "${MIGASFREE_CONF_DIR}"

export MIGASFREE_PUBLIC_DIR=/var/migasfree/public
mkdir -p "$(dirname "${MIGASFREE_PUBLIC_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/public" "${MIGASFREE_PUBLIC_DIR}"

export MIGASFREE_POOL_DIR=/var/migasfree/pool
mkdir -p "$(dirname "${MIGASFREE_POOL_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/pool" "${MIGASFREE_POOL_DIR}"

_CONTAINER=$(hostname)
sed -i "s/@container@/$_CONTAINER/g" /var/migasfree/404.html
sed -i "s/@container@/$_CONTAINER/g" /var/migasfree/50x.html

# TODO: Remove link. Warning!!! Afect to symbolic links of packages in REPOSITORIES.
# ¿Changes MIGASFREE_PUBLIC_DIR = '/var/migasfree/repo' in source?
ln -snf /var/migasfree/public /var/migasfree/repo

send_message "waiting core"
wait_for_service core 8080

show_banner "$(nginx -v 2>&1)"

# Reload extensions for haproxy.cfg (even if named haproxy, it seems to be used here)
# ======================================
/usr/bin/update_extensions.sh

# Get external deployments extensions from manager
# ================================================
curl -s http://manager:8080/manager/v1/private/nginx_extensions > /var/tmp/external-deployments.conf || :

send_message ""

exec nginx -g 'daemon off;'

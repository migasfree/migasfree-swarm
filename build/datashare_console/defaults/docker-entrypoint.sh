#!/bin/sh
set -e

. /usr/bin/common.sh
export MIGASFREE_SECRET_DIR=/var/run/secrets

start_message
set_tz

show_banner "FileBrowser Quantum $(/bin/filebrowser version 2>&1 | head -n 1)"

init_datashare() {
    # Structure of paths in datashare

    # conf
    mkdir -p ${_ROOT}/conf/ || :

    #dump
    mkdir -p ${_ROOT}/dump || :

    # public
    mkdir -p ${_ROOT}/public || :

    # pool
    mkdir -p ${_ROOT}/pool/install || :

    # keys
    mkdir -p ${_ROOT}/keys || :

    # tmp
    mkdir -p ${_ROOT}/tmp || :

    # consoles
    mkdir -p ${_ROOT}/consoles/datashare || :
    mkdir -p ${_ROOT}/consoles/datastore || :
    mkdir -p ${_ROOT}/consoles/database || :

    # plugins
    mkdir -p ${_ROOT}/plugins || :

    # ca-certificates
    mkdir -p ${_ROOT}/ca-certificates || :

    # Changes owner if neccesary (local volume)
    OWN=$(stat -c '%u' ${_ROOT}/keys)
    if ! [ "${OWN}" = "890" ]
    then
        chown -R 890:890  ${_ROOT}/*
    fi

    # /pool/install
    if [ "${HTTPSMODE}" = "manual" ]
    then
        cp "/mnt/cluster/certificates/${STACK}/ca/ca.crt" "${_ROOT}/pool/install/ca-${FQDN}.crt"

        cat <<-EOF > "${_ROOT}/pool/install/migasfree-client.txt"
# Run as root

# The public certificate from the certification authority is required.
wget --no-check-certificate -O /usr/local/share/ca-certificates/ca-${FQDN}.crt https://${FQDN}/manager/v1/public/ca
/sbin/update-ca-certificates --fresh

# Install migasfree-client:
wget -O - https://migasfree.org/pub/install-client | bash

# Configure the Server in /etc/migasfree.conf
sed -i 's/# Server = localhost/Server = ${FQDN}:443/g' /etc/migasfree.conf
EOF
    else
        cat <<-EOF > "${_ROOT}/pool/install/migasfree-client.txt"
# Run as root

# Install migasfree-client:
wget -O - https://migasfree.org/pub/install-client | bash

# Configure the Server in /etc/migasfree.conf
sed -i 's/# Server = localhost/Server = ${FQDN}:443/g' /etc/migasfree.conf
EOF
    fi
    chown 890:890 "${_ROOT}/pool/install/"*
}

waiting_fs() {
    if [ "${DATASHARE_FS}" = "nfs" ]
    then
        echo "waiting NFS..."
        while true
        do
            RET=$(mount | grep " type nfs4 " | grep /mnt/cluster) || :
            if ! [ -z "$RET" ]
            then
                break
            else
                send_message "NFS disconnected"
                echo "$(date) NFS disconnected"
                sleep 5
            fi
        done
    fi
}

# CONFIG
_ROOT="/srv"
_DATABASE="${_ROOT}/consoles/datashare/database.db"
_CONFIG="/config/config.yaml"

waiting_fs
init_datashare

mkdir -p /config
cat << EOF > "${_CONFIG}"
server:
  port: 80
  baseURL: "/"
  logging:
    - levels: "info|warning|error"
  sources:
    - path: "${_ROOT}"
auth:
  methods:
    password:
      enabled: true
      minLength: 5
      signup: false
    passkey:
      enabled: false
EOF

chown -R user:user /config "${_ROOT}/consoles/datashare"

export FILEBROWSER_CONFIG="${_CONFIG}"
export FILEBROWSER_DATABASE="${_DATABASE}"

_ADMIN_NAME=$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_name")
_ADMIN_PASS=$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")

if ! [ -f "${_DATABASE}" ]
then
    su user -c "cd /home/filebrowser && FILEBROWSER_CONFIG=${_CONFIG} FILEBROWSER_DATABASE=${_DATABASE} /home/filebrowser/filebrowser set -u ${_ADMIN_NAME},${_ADMIN_PASS} -a"
fi

send_message ""

cd /home/filebrowser
exec su user -c "cd /home/filebrowser && FILEBROWSER_CONFIG=${_CONFIG} FILEBROWSER_DATABASE=${_DATABASE} /home/filebrowser/filebrowser"

#!/bin/sh
set -e


MIGASFREE_SECRET_DIR=/var/run/secrets

set_TZ() {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime || :
}

send_message "starting ${SERVICE:(${#STACK})+1}"

set_TZ

send_message "init datashare"

echo "


                   █                          ██
                                             █
         ███ ██    █    ██     ███     ███  ████  ███  ███    ███
        █   █  █   █   █  █       █   █      █   █    █   █  █   █
        █   █  █   █   █  █    ████    ██    █   █    ████   ████
        █   █  █   █   █  █   █   █      █   █   █    █      █
        █   █  █   █    ███    ███    ███    █   █     ███    ███
                          █
        we love change  ██


        $SERVICE ($TAG)
        $(filebrowser version)
        Container: $HOSTNAME
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

init_datashare() {
    # Structure of paths in datashare

    # conf
    mkdir -p ${_ROOT}/conf/ || :

    if ! [ -f ${_ROOT}/conf/settings.py ]
    then
        cp /etc/migasfree/settings.py ${_ROOT}/conf/
    fi

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
        cp /mnt/cluster/certificates/${STACK}/ca/ca.crt ${_ROOT}/pool/install/ca-${FQDN}.crt

        cat <<-EOF > ${_ROOT}/pool/install/migasfree-client.txt
# Run as root

# The public certificate from the certification authority is required.
wget --no-check-certificate -O /usr/local/share/ca-certificates/ca-${FQDN}.crt https://${FQDN}/pool/install/ca-${FQDN}.crt
update-ca-certificates --fresh

# Install migasfree-client:
wget -O - https://migasfree.org/pub/install-client | bash

# Configure the Server in /etc/migasfree.conf
sed -i 's/# Server = localhost/Server = ${FQDN}:443/g' /etc/migasfree.conf
EOF
    else
        cat <<-EOF > ${_ROOT}/pool/install/migasfree-client.txt
# Run as root

# Install migasfree-client:
wget -O - https://migasfree.org/pub/install-client | bash

# Configure the Server in /etc/migasfree.conf
sed -i 's/# Server = localhost/Server = ${FQDN}:443/g' /etc/migasfree.conf
EOF
    fi
    chown 890:890 ${_ROOT}/pool/install/*
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

waiting_fs
init_datashare

cat << EOF > /.filebrowser.json
{
  "port": 80,
  "baseURL": "",
  "address": "",
  "log": "stdout",
  "database": "${_DATABASE}",
  "root": "${_ROOT}"
}
EOF

if ! [ -f ${_DATABASE} ]
then
    su user -c "/bin/filebrowser config init --branding.name datashare"
    su user -c "/bin/filebrowser users add $(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_name) $(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass) --perm.admin"
fi

send_message ""

su user -c "/bin/filebrowser"

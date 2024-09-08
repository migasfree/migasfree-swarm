#!/bin/sh
trap exit TERM

export MIGASFREE_CERTIFICATES_DIR=/etc/certificates
mkdir -p $(dirname ${MIGASFREE_CERTIFICATES_DIR})
ln -s /mnt/datashare/certificates ${MIGASFREE_CERTIFICATES_DIR}

while :;
do
    send_message "renew certificate letsencript" 
    [ "${HTTPSMODE}" = "auto" ] && . /usr/bin/renew-certificates.sh
    send_message ""
    sleep 12h & wait ${!}
done

#!/bin/sh

# Request certificates if they don't exist on volume
if [ ! -f /etc/certificates/${STACK}.pem ]; then
    certbot certonly --standalone \
    --non-interactive --agree-tos --email ${EMAIL} --http-01-port=380 \
    --cert-name ${FQDN} \
    -d ${FQDN} -d portainer.${FQDN} -d datastore.${FQDN} -d database.${FQDN} -d datashare.${FQDN} -d worker.${FQDN}

    # Concatenate certificates
    . /usr/bin/concatenate-certificates.sh
fi
# Update certificates in HAProxy
[ -f /etc/certificates/${STACK}.pem ] && . /usr/bin/update-haproxy-certificates.sh
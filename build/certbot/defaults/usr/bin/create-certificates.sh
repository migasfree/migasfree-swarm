#!/bin/sh

# Request certificates
certbot certonly --standalone \
--non-interactive --agree-tos --email ${EMAIL} --http-01-port=380 \
--cert-name ${FQDN} \
-d ${FQDN} -d portainer.${FQDN} -d datastore.${FQDN} -d database.${FQDN} -d datashare.${FQDN} -d worker.${FQDN}

# Concatenate certificates
. /usr/bin/concatenate-certificates.sh

# Update certificates in HAProxy
. /usr/bin/update-haproxy-certificates.sh
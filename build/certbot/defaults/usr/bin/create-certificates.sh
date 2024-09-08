#!/bin/bash

# Request certificates
certbot certonly --standalone \
--non-interactive --agree-tos --email ${EMAIL} --http-01-port=380 \
--cert-name ${FQDN} \
-d ${FQDN}

# Concatenate certificates
. /usr/bin/concatenate-certificates.sh

# Update certificates in HAProxy
. /usr/bin/update-haproxy-certificates.sh
#!/bin/sh

# Request certificates from Let's Encrypt
certbot certonly --standalone \
    --non-interactive --agree-tos --http-01-port=380 \
    --cert-name "${FQDN}" \
    -d "${FQDN}" -d "portainer-${FQDN}" -d "datastore-${FQDN}" -d "database-${FQDN}" -d "datashare-${FQDN}" -d "worker-${FQDN}"

# Concatenate certificates
# shellcheck source=/dev/null
. /usr/bin/concatenate-certificates.sh

# Update certificates in HAProxy
# shellcheck source=/dev/null
[ -f "/etc/certificates/${STACK}.pem" ] && . /usr/bin/update-haproxy-certificates.sh

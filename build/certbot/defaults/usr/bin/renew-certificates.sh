#!/bin/sh

# Certificates exist
if [ -d /etc/letsencrypt/live/${FQDN} ]; then
    # Check certificates and renew them
    certbot renew --http-01-port=380

    # Concatenate certificates
    . /usr/bin/concatenate-certificates.sh

    # Update certificates in HAProxy
    . /usr/bin/update-haproxy-certificates.sh

    # Certificates don't exist
else
    #  Execute certificate creation script
    . /usr/bin/create-certificates.sh
fi
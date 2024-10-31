#!/bin/sh

# Certificates exist
if [ -d /etc/letsencrypt/live/${FQDN} ]; then
    if [ ! -f /etc/letsencrypt/live/${FQDN}/fullchain.pem.md5 ]; then
        md5sum /etc/letsencrypt/live/${FQDN}/fullchain.pem >/etc/letsencrypt/live/${FQDN}/fullchain.pem.md5
    fi
    # Check certificates and renew them
    certbot renew --http-01-port=380
    if ! md5sum -c /etc/letsencrypt/live/${FQDN}/fullchain.pem.md5; then
        md5sum /etc/letsencrypt/live/${FQDN}/fullchain.pem >/etc/letsencrypt/live/${FQDN}/fullchain.pem.md5
        
        echo "Certificates have been renewed"
        
        # Concatenate certificates
        . /usr/bin/concatenate-certificates.sh
        
        echo "Renewed certificates to HAProxy"
        # Update certificates in HAProxy
        [ -f /etc/certificates/${STACK}.pem ] && . /usr/bin/update-haproxy-certificates.sh
    fi

# Certificates don't exist
else
    #  Execute certificate creation script
    . /usr/bin/create-certificates.sh
fi

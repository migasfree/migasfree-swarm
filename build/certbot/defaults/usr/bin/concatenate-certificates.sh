#!/bin/sh

if [ -f /etc/letsencrypt/live/${FQDN}/fullchain.pem ] && [ -f /etc/letsencrypt/live/${FQDN}/privkey.pem ]; then
    cat /etc/letsencrypt/live/${FQDN}/fullchain.pem /etc/letsencrypt/live/${FQDN}/privkey.pem > /etc/certificates/${STACK}.pem
fi
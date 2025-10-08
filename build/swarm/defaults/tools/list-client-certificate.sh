#!/bin/sh

PATH_CA="/mnt/cluster/certificates"
PATH_MTLS="${PATH_CA}/mtls/certs"
cd ${PATH_MTLS}

echo

for certfile in *.crt; do


    cn=$(openssl x509 -in "$certfile" -noout -subject | sed -n 's/.*CN=\([^,]*\).*/\1/p')
    cert_id=$(openssl x509 -in "$certfile" -noout -serial 2>/dev/null | sed 's/serial=//')
    email=$(openssl x509 -in "$certfile" -noout -text | grep "X509v3 Subject Alternative Name" -A1 | grep email: | sed 's/.*email://')
    issuance=$(openssl x509 -in "$certfile" -noout -startdate 2>/dev/null)
    expiry=$(openssl x509 -in "$certfile" -noout -enddate 2>/dev/null)

    echo "                    File: $certfile"
    echo "        Certificate Name: ${cn}"
    echo "          Certificate ID: ${cert_id}"
    echo "                   email: ${email}"
    echo "              Issue date: ${issuance#*=}"
    echo "             Expiry date: ${expiry#*=}"
    echo ""

done
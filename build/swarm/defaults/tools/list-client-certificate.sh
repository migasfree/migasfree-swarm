#!/bin/sh

PATH_CA="/mnt/cluster/certificates"
PATH_MTLS="${PATH_CA}/mtls/certs"
cd ${PATH_MTLS}

echo

for certfile in *.crt; do

    echo "$certfile"
    cert_id=$(openssl x509 -in "$certfile" -noout -serial 2>/dev/null | sed 's/serial=//')
    issuance=$(openssl x509 -in "$certfile" -noout -startdate 2>/dev/null)
    expiry=$(openssl x509 -in "$certfile" -noout -enddate 2>/dev/null)
    echo "    Certificate ID: $cert_id"
    echo "        Issue date: ${issuance#*=}"
    echo "       Expiry date: ${expiry#*=}"
    echo ""

done
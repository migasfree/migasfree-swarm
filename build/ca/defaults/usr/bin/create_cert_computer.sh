#!/bin/sh


FQDN="$1"
HOST="$2"
STACK="$3"
UUID="$4"
PASSWORD="$5"
DAYS_VALID="$6"
EMAIL="$7"


CERT_NAME="${UUID}"

if [ -z "${DAYS_VALID}" ]; then
   DAYS_VALID="7305"
fi

PATH_CA="/mnt/cluster/certificates/${STACK}/ca"
PATH_RESOURCE="/mnt/cluster/certificates/${STACK}/computer"
PATH_CERTS="/mnt/cluster/certificates/${STACK}/computer/certs"


CA_CERT="${PATH_CA}/ca.crt"       # CA Certificate
CA_KEY="${PATH_CA}/ca.key"        # CA Private Key
CONFIG_EXT="${PATH_CERTS}/${CERT_NAME}.cnf"


cd ${PATH_CERTS}

cat > $CONFIG_EXT <<EOF
[ v3_ext ]
extendedKeyUsage = clientAuth, 1.2.3.4.5.6.7.8.2
subjectAltName = DNS:${FQDN}, email:copy
crlDistributionPoints = URI:http://${HOST}/ca/v1/public/crl

EOF


# Generate client private key protected with password
openssl genrsa -aes256 -passout pass:$PASSWORD -out ${CERT_NAME}.key 2048

# Generate CSR with private key
openssl req -new -key ${CERT_NAME}.key -passin pass:$PASSWORD -out ${CERT_NAME}.csr -subj "/emailAddress=${EMAIL}/CN=${CERT_NAME}/OU=COMPUTERS"

# Sign the CSR with the CA to create the client certificate
openssl ca -config ${PATH_RESOURCE}/openssl.cnf -extensions v3_ext -extfile $CONFIG_EXT \
    -in ${CERT_NAME}.csr -out ${CERT_NAME}.crt -days $DAYS_VALID -batch

# Create PKCS#12 file for import (contains private key and certificate)
openssl pkcs12 -export -out ${CERT_NAME}.p12 -inkey ${CERT_NAME}.key -passin pass:$PASSWORD -in ${CERT_NAME}.crt -certfile $CA_CERT -passout pass:$PASSWORD

echo "


                   █                          ██
                                             █
         ███ ██    █    ██     ███     ███  ████  ███  ███    ███
        █   █  █   █   █  █       █   █      █   █    █   █  █   █
        █   █  █   █   █  █    ████    ██    █   █    ████   ████
        █   █  █   █   █  █   █   █      █   █   █    █      █
        █   █  █   █    ███    ███    ███    █   █     ███    ███
                          █
                        ██



Wellcome to migasfree, we love change !!!

To access the migasfree console, the use of a mutual TLS (mTLS) certificate is required. This ensures
a secure connection where both the user and the server verify each other's identity, protecting access
and data exchange.

Steps to Import your Personal Digital Certificate (mTLS) in Mozilla Firefox
===========================================================================

To import '${CERT_NAME}.p12' certificate file into Mozilla Firefox, follow these steps:

    1. Open Firefox and go to the menu (three horizontal lines in the upper right corner).

    2. Select 'Settings' or 'Options.'

    3. Navigate to 'Privacy & Security.'

    4. Scroll down and click on the 'View Certificates' button under the Certificates section.

    5. In the Certificate Manager window, go to the 'Your Certificates' tab.

    6. Click the 'Import' button.

    7. Browse to locate your '${CERT_NAME}.p12' file and select it.

    8. Enter the password used to protect the certificate when prompted.

    9. Confirm the import and check that the certificate appears under 'Your Certificates'.

    10. Click OK and restart Firefox.

    11. Visit https://${HOST}/

    (In other web browsers, the steps are quite similar)

" > ${CERT_NAME}.README

cn=$(openssl x509 -in "${CERT_NAME}.crt" -noout -subject | sed -n 's/.*CN=\([^,]*\).*/\1/p')
cert_id=$(openssl x509 -in "${CERT_NAME}.crt" -noout -serial 2>/dev/null | sed 's/serial=//')
dns=$(openssl x509 -in "${CERT_NAME}.crt"  -noout -ext subjectAltName | grep -oE 'DNS:[^,]+' | sed 's/DNS://')
email=$(openssl x509 -in "${CERT_NAME}.crt" -noout -text | grep "X509v3 Subject Alternative Name" -A1 | grep email: | sed 's/.*email://')
issuance=$(openssl x509 -in "${CERT_NAME}.crt" -noout -startdate 2>/dev/null)
expiry=$(openssl x509 -in "${CERT_NAME}.crt" -noout -enddate 2>/dev/null)

echo ""
echo "                    File: ${CERT_NAME}.p12" >> ${CERT_NAME}.README
echo "          Certificate ID: ${cert_id}" >> ${CERT_NAME}.README
echo "             Common Name: ${cn}" >> ${CERT_NAME}.README
echo "                DNS Name: ${dns}" >> ${CERT_NAME}.README
echo "                   email: ${email}" >> ${CERT_NAME}.README
echo "              Issue date: ${issuance#*=}" >> ${CERT_NAME}.README
echo "             Expiry date: ${expiry#*=}" >> ${CERT_NAME}.README
echo ""

tar -cvf ${CERT_NAME}.tar ${CERT_NAME}.p12 ${CERT_NAME}.README

rm ${CERT_NAME}.p12
rm ${CERT_NAME}.README
rm ${CERT_NAME}.key
rm ${CERT_NAME}.csr
rm ${CERT_NAME}.cnf

#!/bin/bash



USER="$1"
FQDN="$2"
PASSWORD="$3"
DAYS_VALID="$4"
EMAIL="$5"

CERT_NAME="${USER}-${FQDN}"

if [ -z "${DAYS_VALID}" ]; then
   DAYS_VALID="7305"
fi

PATH_CA="/mnt/cluster/certificates"
PATH_MTLS="${PATH_CA}/mtls/certs"


CA_CERT="${PATH_CA}/ca.crt"       # CA Certificate
CA_KEY="${PATH_CA}/ca.key"        # CA Private Key
CONFIG_EXT="${CERT_NAME}_ext.cnf"


mkdir -p ${PATH_MTLS}
cd ${PATH_MTLS}

cat > $CONFIG_EXT <<EOF
[ v3_ext ]
extendedKeyUsage = clientAuth
subjectAltName = email:copy
crlDistributionPoints = URI:http://${FQDN}/services/crl
EOF


# Generate client private key protected with password
openssl genrsa -aes256 -passout pass:$PASSWORD -out ${CERT_NAME}.key 2048

# Generate CSR with private key
openssl req -new -key ${CERT_NAME}.key -passin pass:$PASSWORD -out ${CERT_NAME}.csr -subj "/emailAddress=${EMAIL}/CN=${CERT_NAME}"

# Sign the CSR with the CA to create the client certificate
openssl ca -config ${PATH_CA}/mtls/mtls.cnf -extensions v3_ext -extfile $CONFIG_EXT \
    -in ${CERT_NAME}.csr -out ${CERT_NAME}.crt -days $DAYS_VALID -batch

# Create PKCS#12 file for import (contains private key and certificate)
openssl pkcs12 -export -out ${CERT_NAME}.p12 -inkey ${CERT_NAME}.key -passin pass:$PASSWORD -in ${CERT_NAME}.crt -certfile $CA_CERT -passout pass:$PASSWORD

echo "

Steps to Import your Personal Digital Certificate in Mozilla Firefox
====================================================================

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

    11. Visit https://${FQDN}/  (User: ${USER})

    (In other web browsers, the steps are quite similar)

" > README

cn=$(openssl x509 -in "${CERT_NAME}.crt" -noout -subject | sed -n 's/.*CN=\([^,]*\).*/\1/p')
cert_id=$(openssl x509 -in "${CERT_NAME}.crt" -noout -serial 2>/dev/null | sed 's/serial=//')
email=$(openssl x509 -in "${CERT_NAME}.crt" -noout -text | grep "X509v3 Subject Alternative Name" -A1 | grep email: | sed 's/.*email://')
issuance=$(openssl x509 -in "${CERT_NAME}.crt" -noout -startdate 2>/dev/null)
expiry=$(openssl x509 -in "${CERT_NAME}.crt" -noout -enddate 2>/dev/null)

echo ""
echo "                    File: ${CERT_NAME}.p12" >> README
echo "        Certificate Name: ${cn}" >> README
echo "          Certificate ID: ${cert_id}" >> README
echo "                   email: ${email}" >> README
echo "              Issue date: ${issuance#*=}" >> README
echo "             Expiry date: ${expiry#*=}" >> README
echo ""

tar -cvf ${CERT_NAME}.tar ${CERT_NAME}.p12 README

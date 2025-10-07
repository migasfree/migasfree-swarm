#!/bin/bash

CLIENT_NAME="$1"
PASSWORD="$2"
DAYS_VALID="$3"

if [ -z "${DAYS_VALID}" ]; then
   DAYS_VALID="7300"
fi

PATH_CA="/mnt/cluster/certificates"
PATH_MTLS="${PATH_CA}/mtls/certs"


CA_CERT="${PATH_CA}/ca.crt"       # CA Certificate
CA_KEY="${PATH_CA}/ca.key"        # CA Private Key
CONFIG_EXT="${CLIENT_NAME}_ext.cnf"


mkdir -p ${PATH_MTLS}
cd ${PATH_MTLS}

cat > $CONFIG_EXT <<EOF
[ v3_ext ]
extendedKeyUsage = clientAuth
crlDistributionPoints = URI:http://${FQDN}/services/crl
EOF


# Generate client private key protected with password
openssl genrsa -aes256 -passout pass:$PASSWORD -out ${CLIENT_NAME}.key 2048

# Generate CSR with private key
openssl req -new -key ${CLIENT_NAME}.key -passin pass:$PASSWORD -out ${CLIENT_NAME}.csr -subj "/CN=${CLIENT_NAME}"

# Sign the CSR with the CA to create the client certificate
#openssl x509 -req -in ${CLIENT_NAME}.csr -CA $CA_CERT -CAkey $CA_KEY -CAcreateserial \
#    -out ${CLIENT_NAME}.crt -days $DAYS_VALID -sha256 -extfile $CONFIG_EXT -extensions v3_ext

openssl ca -config ${PATH_CA}/mtls/mtls.cnf -extensions v3_ext -extfile $CONFIG_EXT \
    -in ${CLIENT_NAME}.csr -out ${CLIENT_NAME}.crt -days $DAYS_VALID -batch



# Create PKCS#12 file for import (contains private key and certificate)
openssl pkcs12 -export -out ${CLIENT_NAME}.p12 -inkey ${CLIENT_NAME}.key -passin pass:$PASSWORD -in ${CLIENT_NAME}.crt -certfile $CA_CERT -passout pass:$PASSWORD

echo "

Steps to Import your Personal Digital Certificate in Mozilla Firefox
====================================================================

To import '${CLIENT_NAME}.p12' certificate file into Mozilla Firefox, follow these steps:

    1. Open Firefox and go to the menu (three horizontal lines in the upper right corner).

    2. Select 'Settings' or 'Options.'

    3. Navigate to 'Privacy & Security.'

    4. Scroll down and click on the 'View Certificates' button under the Certificates section.

    5. In the Certificate Manager window, go to the 'Your Certificates' tab.

    6. Click the 'Import' button.

    7. Browse to locate your '${CLIENT_NAME}.p12' file and select it.

    8. Enter the password used to protect the certificate when prompted.

    9. Confirm the import and check that the certificate appears under 'Your Certificates'.

    10. Click OK and restart Firefox.

    11. Visit https://${FQDN}/

In other web browsers, the steps are quite similar.

" > README

cert_id=$(openssl x509 -in "${CLIENT_NAME}.crt" -noout -serial 2>/dev/null | sed 's/serial=//')
issuance=$(openssl x509 -in "${CLIENT_NAME}.crt" -noout -startdate 2>/dev/null)
expiry=$(openssl x509 -in "${CLIENT_NAME}.crt" -noout -enddate 2>/dev/null)


echo "${CLIENT_NAME}" >> README
echo "    Certificate ID: $cert_id" >> README
echo "        Issue date: ${issuance#*=}" >> README
echo "       Expiry date: ${expiry#*=}" >> README
echo ""

tar -cvf ${CLIENT_NAME}.tar ${CLIENT_NAME}.p12 README

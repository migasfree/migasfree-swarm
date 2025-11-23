#!/bin/sh

FQDN="$1"
STACK="$2"

PATH_CA=/mnt/cluster/certificates/${STACK}/ca
PATH_SERVER=/mnt/cluster/certificates/${STACK}/server
DAYS=7305  # 20 years

mkdir -p ${PATH_SERVER}
cd ${PATH_SERVER}

if ! [ -f ${PATH_SERVER}/${FQDN}.pem ]
then

    # Create a CSR:
    openssl req -newkey rsa:2048 -nodes -sha256 -keyout ${FQDN}.key -out ${FQDN}.csr -subj "/C=ES/ST=ZARAGOZA/L=ZARAGOZA/O=migasfree/OU=Core/CN=${FQDN}"

    # Check contents of CSR (optional):
    # openssl req -in ${FQDN}.csr -text -noout

    # Sign the CSR, resulting in CRT and add the v3 SAN extension:
    SAN="DNS.1=${FQDN}\nDNS.2=*.${FQDN}\n"
    openssl x509 -req -in ${FQDN}.csr -out ${FQDN}.crt -CA ${PATH_CA}/ca.crt -CAkey ${PATH_CA}/ca.key -CAcreateserial -sha256 -days $DAYS -extensions SAN -extfile <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=@san_names\nbasicConstraints=CA:FALSE\nkeyUsage=nonRepudiation,digitalSignature,keyEncipherment\n[san_names]\n${SAN}"))

    chmod 600 ${FQDN}.key

    # Check contents of CRT (optional)
    openssl x509 -in ${FQDN}.crt -text -noout

    # Certificate autosigned for TSL in haproxy (Private Key + Certificate)
    cat ${FQDN}.key ${FQDN}.crt > ${FQDN}.pem
    chmod 600 ${FQDN}.pem
fi




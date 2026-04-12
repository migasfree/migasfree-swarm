#!/bin/sh

FQDN="$1"
STACK="$2"

PATH_CA=/mnt/cluster/certificates/${STACK}/ca
PATH_SERVER=/mnt/cluster/certificates/${STACK}/server
DAYS=7305  # 20 years

mkdir -p "${PATH_SERVER}"
cd "${PATH_SERVER}" || exit 1

if ! [ -f "${PATH_SERVER}/${FQDN}.pem" ]
then

    # Create a CSR:
    openssl req -newkey rsa:2048 -nodes -sha256 -keyout "${FQDN}.key" -out "${FQDN}.csr" -subj "/C=ES/ST=ZARAGOZA/L=ZARAGOZA/O=migasfree/OU=Core/CN=${FQDN}"

    # Check contents of CSR (optional):
    # openssl req -in ${FQDN}.csr -text -noout

    # Sign the CSR, resulting in CRT and add the v3 SAN extension:
    _EXTFILE=$(mktemp)
    cat /etc/ssl/openssl.cnf > "$_EXTFILE"
    printf "[SAN]\nsubjectAltName=@san_names\nbasicConstraints=CA:FALSE\nkeyUsage=nonRepudiation,digitalSignature,keyEncipherment\n[san_names]\nDNS.1=%s\nDNS.2=*.%s\n" "$FQDN" "$FQDN" >> "$_EXTFILE"
    openssl x509 -req -in "${FQDN}.csr" -out "${FQDN}.crt" -CA "${PATH_CA}/ca.crt" -CAkey "${PATH_CA}/ca.key" -CAcreateserial -sha256 -days "$DAYS" -extensions SAN -extfile "$_EXTFILE"
    rm "$_EXTFILE"

    chmod 600 "${FQDN}.key"

    # Check contents of CRT (optional)
    openssl x509 -in "${FQDN}.crt" -text -noout

    # Certificate autosigned for TSL in haproxy (Private Key + Certificate)
    cat "${FQDN}.key" "${FQDN}.crt" > "${FQDN}.pem"
    chmod 600 "${FQDN}.pem"
fi

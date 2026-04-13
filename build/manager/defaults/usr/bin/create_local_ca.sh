#!/bin/sh
. /usr/bin/common.sh

PATH_CA=/mnt/cluster/certificates/${STACK}/ca
PATH_ADMIN=/mnt/cluster/certificates/${STACK}/admin
PATH_COMPUTER=/mnt/cluster/certificates/${STACK}/computer

DAYS=7305  # 20 years

mkdir -p "$PATH_CA"

exit_on_error() {
    echo "Error: $1"
    exit 1
}

# Helper function to initialize a CA resource (directory structure and openssl.cnf)
init_ca_resource() {
    _PATH="$1"
    _TYPE="$2"

    log_info "Initializing CA resource structure for ${_TYPE} in ${_PATH}..."
    mkdir -p "${_PATH}/certs" "${_PATH}/crl" "${_PATH}/newcerts" "${_PATH}/private"
    touch "${_PATH}/index.txt"
    [ ! -f "${_PATH}/serial" ] && echo 1000 > "${_PATH}/serial"
    [ ! -f "${_PATH}/crlnumber" ] && echo 1000 > "${_PATH}/crlnumber"

    cat <<EOF > "${_PATH}/openssl.cnf"
[ ca ]
default_ca = CA_default

[ CA_default ]
dir_ca               = ${PATH_CA}
dir_resource         = ${_PATH}

certs             = \$dir_resource/certs
crl_dir           = \$dir_resource/crl
database          = \$dir_resource/index.txt
new_certs_dir     = \$dir_resource/newcerts
certificate       = \$dir_ca/ca.crt
serial            = \$dir_resource/serial
crlnumber         = \$dir_resource/crlnumber
crl               = \$dir_resource/crl.pem
private_key       = \$dir_ca/ca.key
RANDFILE          = \$dir_resource/private/.rand

default_days      = ${DAYS}
default_crl_days  = 30
default_md        = sha256
unique_subject    = no

policy            = policy_anything
email_in_dn       = no

[policy_anything]
countryName             = optional
stateOrProvinceName     = optional
localityName            = optional
organizationName        = optional
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional
EOF

    chmod 700 "${_PATH}/private"
    chmod 755 "${_PATH}/newcerts"
    chmod 644 "${_PATH}/serial" "${_PATH}/index.txt"

    # Create initial CRL
    openssl ca -config "${_PATH}/openssl.cnf" -gencrl -out "${_PATH}/crl/crl.pem"

    chown -R 890:890 "${_PATH}"
    log_success "CA resource structure for ${_TYPE} initialized."
}

# 1. Initialize CA
mkdir -p "$PATH_CA"
if ! [ -f "${PATH_CA}/ca.key" ]
then
    cd "${PATH_CA}" || exit_on_error "Could not access CA path"
    log_info "Generating Root CA..."
    cat <<EOF > ca_openssl.cnf
[ req ]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[ req_distinguished_name ]
C = ES
ST = ZARAGOZA
L = ZARAGOZA
O = migasfree
CN = ${FQDN} Root CA

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
EOF

    openssl req -new -x509 -nodes -newkey rsa:4096 -config ca_openssl.cnf -sha256 -days $DAYS -keyout ca.key -out ca.crt
    chmod 600 ca.key
    log_success "Root CA generated."
fi

# 2. Initialize Server Certificate
/usr/bin/create_cert_server.sh "${FQDN}" "${STACK}"

# 3. Initialize Admin CA Resource
if ! [ -f "${PATH_ADMIN}/openssl.cnf" ]
then
    init_ca_resource "${PATH_ADMIN}" "Admin"
fi

# 4. Initialize Computer CA Resource
if ! [ -f "${PATH_COMPUTER}/openssl.cnf" ]
then
    init_ca_resource "${PATH_COMPUTER}" "Computer"
fi

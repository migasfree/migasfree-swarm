#!/bin/sh

PATH_CA=/mnt/cluster/certificates/${STACK}/ca
PATH_ADMIN=/mnt/cluster/certificates/${STACK}/admin
PATH_COMPUTER=/mnt/cluster/certificates/${STACK}/computer

DAYS=7305  # 20 years

mkdir -p $PATH_CA

if ! [ -f ${PATH_CA}/ca.key ]
then
    cd ${PATH_CA}
    # Create the CA certificate and key:
    openssl req -new -x509 -nodes -newkey rsa:4096 -extensions v3_ca -sha256 -days $DAYS -subj "/C=ES/ST=ZARAGOZA/L=ZARAGOZA/O=migasfree/CN=${FQDN} Root CA" -keyout ca.key -out ca.crt
    chmod 600 ca.key
fi


/usr/bin/create_cert_server.sh ${FQDN} ${STACK}



# Config for Admin Certificate mTLS
# ================================
mkdir -p ${PATH_ADMIN}
cd ${PATH_ADMIN}

if ! [ -f "${PATH_ADMIN}/openssl.cnf" ];
then
    echo "[ ca ]
default_ca = CA_default

[ CA_default ]
# Directorio base para archivos de la CA
dir_ca               = ${PATH_CA}
dir_resource         = ${PATH_ADMIN}

# Rutas a archivos y carpetas importantes
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

# Parámetros por defecto para la emisión
default_days      = ${DAYS}
default_crl_days  = 30
default_md        = sha256
unique_subject    = no

# Políticas de firma
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


" > "${PATH_ADMIN}/openssl.cnf"

    mkdir -p ${PATH_ADMIN}/certs
    mkdir -p ${PATH_ADMIN}/crl
    mkdir -p ${PATH_ADMIN}/newcerts
    mkdir -p ${PATH_ADMIN}/private
    touch "${PATH_ADMIN}/index.txt"

    echo 1000 > "${PATH_ADMIN}/serial"
    echo 1000 > "${PATH_ADMIN}/crlnumber"

    chmod 700 ${PATH_ADMIN}/private
    chmod 755 ${PATH_ADMIN}/newcerts
    chmod 644 ${PATH_ADMIN}/serial
    chmod 644 ${PATH_ADMIN}/index.txt

    # create crl
    openssl ca -config "${PATH_ADMIN}/openssl.cnf" -gencrl -out "${PATH_ADMIN}/crl/crl.pem"

    chown -R 890:890 "${PATH_ADMIN}"

fi




# Config for Computer Certificate mTLS
# ====================================
mkdir -p ${PATH_COMPUTER}
cd ${PATH_COMPUTER}

if ! [ -f "${PATH_COMPUTER}/openssl.cnf" ];
then
    echo "[ ca ]
default_ca = CA_default

[ CA_default ]
# Directorio base para archivos de la CA
dir_ca               = ${PATH_CA}
dir_resource             = ${PATH_COMPUTER}

# Rutas a archivos y carpetas importantes
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

# Parámetros por defecto para la emisión
default_days      = ${DAYS}
default_crl_days  = 30
default_md        = sha256
unique_subject    = no

# Políticas de firma
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

" > "${PATH_COMPUTER}/openssl.cnf"

    mkdir -p ${PATH_COMPUTER}/certs
    mkdir -p ${PATH_COMPUTER}/crl
    mkdir -p ${PATH_COMPUTER}/newcerts
    mkdir -p ${PATH_COMPUTER}/private
    touch "${PATH_COMPUTER}/index.txt"

    echo 1000 > "${PATH_COMPUTER}/serial"
    echo 1000 > "${PATH_COMPUTER}/crlnumber"

    chmod 700 ${PATH_COMPUTER}/private
    chmod 755 ${PATH_COMPUTER}/newcerts
    chmod 644 ${PATH_COMPUTER}/serial
    chmod 644 ${PATH_COMPUTER}/index.txt

    # create crl
    openssl ca -config "${PATH_COMPUTER}/openssl.cnf" -gencrl -out "${PATH_COMPUTER}/crl/crl.pem"

    chown -R 890:890 "${PATH_COMPUTER}"

fi

#!/bin/sh
#
# create_cert_mtls.sh - Generate mTLS client certificate for migasfree admins or computers
#
# Usage: create_cert_mtls.sh TYPE FQDN HOST STACK CERT_NAME PASSWORD [DAYS_VALID] [EMAIL]
#
# Arguments:
#   TYPE       - Type of certificate: 'admin' or 'computer'
#   FQDN       - Fully Qualified Domain Name
#   HOST       - Host for the CRL distribution point
#   STACK      - Stack name for certificate paths
#   CERT_NAME  - Certificate name
#   PASSWORD   - Password for the private key and PKCS#12 file
#   DAYS_VALID - (Optional) Certificate validity in days (default: 7305 = ~20 years)
#   EMAIL      - (Optional) Email address for the certificate
#

. /usr/bin/common.sh
set -e

# ============================================================================
# Configuration
# ============================================================================
SCRIPT_NAME="$(basename "$0")"
DEFAULT_DAYS_VALID="7305"

# ============================================================================
# Functions
# ============================================================================

show_usage() {
    cat <<EOF
Usage: $SCRIPT_NAME TYPE FQDN HOST STACK CERT_NAME PASSWORD [DAYS_VALID] [EMAIL]

Arguments:
  TYPE       - admin | computer
  FQDN       - Fully Qualified Domain Name
  HOST       - Host for the CRL distribution point
  STACK      - Stack name for certificate paths
  CERT_NAME  - Certificate name
  PASSWORD   - Password for the private key
  DAYS_VALID - Certificate validity in days (default: $DEFAULT_DAYS_VALID)
  EMAIL      - Email address for the certificate

Example:
  $SCRIPT_NAME computer example.com console.example.com mystack D11E... secret123 365 user@example.com
EOF
}

validate_arguments() {
    [ -z "${TYPE:-}" ] && { log_error "TYPE is required"; show_usage; exit 1; }
    [ -z "${FQDN:-}" ] && { log_error "FQDN is required"; show_usage; exit 1; }
    [ -z "${HOST:-}" ] && { log_error "HOST is required"; show_usage; exit 1; }
    [ -z "${STACK:-}" ] && { log_error "STACK is required"; show_usage; exit 1; }
    [ -z "${CERT_NAME:-}" ] && { log_error "CERT_NAME is required"; show_usage; exit 1; }
    [ -z "${PASSWORD:-}" ] && { log_error "PASSWORD is required"; show_usage; exit 1; }
    
    case "$TYPE" in
        admin)
            OU="ADMINS"
            OID="1.2.3.4.5.6.7.8.1"
            ;;
        computer)
            OU="COMPUTERS"
            OID="1.2.3.4.5.6.7.8.2"
            ;;
        *)
            log_error "Invalid TYPE: $TYPE. Must be 'admin' or 'computer'."
            exit 1
            ;;
    esac
}

validate_paths() {
    if [ ! -d "$PATH_CERTS" ]; then
        log_error "Certificates directory does not exist: $PATH_CERTS"
        exit 1
    fi
    if [ ! -f "$CA_CERT" ]; then
        log_error "CA certificate not found: $CA_CERT"
        exit 1
    fi
    if [ ! -f "$CA_KEY" ]; then
        log_error "CA private key not found: $CA_KEY"
        exit 1
    fi
    if [ ! -f "${PATH_RESOURCE}/openssl.cnf" ]; then
        log_error "OpenSSL config not found: ${PATH_RESOURCE}/openssl.cnf"
        exit 1
    fi
}

cleanup_temp_files() {
    _exit_code=$?
    log_info "Cleaning up temporary files..."
    cd "$PATH_CERTS" 2>/dev/null || true
    
    # Always cleanup CSR and extension config
    rm -f "${CERT_NAME}.csr" "${CERT_NAME}.cnf" 2>/dev/null || true
    
    if [ $_exit_code -ne 0 ]; then
        # Cleanup everything on failure
        rm -f "${CERT_NAME}.key" "${CERT_NAME}.crt" "${CERT_NAME}.p12" "${CERT_NAME}.tar" "${CERT_NAME}.README" 2>/dev/null || true
        log_error "Certificate generation failed"
    else
        # Only cleanup README if bundled
        [ -f "${CERT_NAME}.README" ] && rm -f "${CERT_NAME}.README"
        log_success "Certificate generation completed successfully!"
    fi
    exit $_exit_code
}

create_extension_config() {
    cat > "$CONFIG_EXT" <<EOF
[ v3_ext ]
extendedKeyUsage = clientAuth, ${OID}
subjectAltName = DNS:${FQDN}, email:copy
crlDistributionPoints = URI:http://${HOST}/manager/v1/public/crl
EOF
}

generate_private_key() {
    log_info "Generating client private key..."
    openssl genrsa -aes256 -passout pass:"$PASSWORD" -out "${CERT_NAME}.key" 2048 2>/dev/null
    log_success "Private key generated"
}

generate_csr() {
    log_info "Generating Certificate Signing Request (CSR)..."
    openssl req -new \
        -key "${CERT_NAME}.key" \
        -passin pass:"$PASSWORD" \
        -out "${CERT_NAME}.csr" \
        -subj "/emailAddress=${EMAIL}/CN=${CERT_NAME}/OU=${OU}/O=${FQDN}"
    log_success "CSR generated"
}

sign_certificate() {
    log_info "Signing certificate with CA (valid for $DAYS_VALID days)..."
    openssl ca \
        -config "${PATH_RESOURCE}/openssl.cnf" \
        -extensions v3_ext \
        -extfile "$CONFIG_EXT" \
        -in "${CERT_NAME}.csr" \
        -out "${CERT_NAME}.crt" \
        -days "$DAYS_VALID" \
        -batch
    log_success "Certificate signed"
}

create_pkcs12() {
    log_info "Creating PKCS#12 bundle..."
    openssl pkcs12 -export \
        -out "${CERT_NAME}.p12" \
        -inkey "${CERT_NAME}.key" \
        -passin pass:"$PASSWORD" \
        -in "${CERT_NAME}.crt" \
        -certfile "$CA_CERT" \
        -passout pass:"$PASSWORD"
    log_success "PKCS#12 bundle created"
}

create_tar_bundle() {
    log_info "Creating tar bundle..."
    if [ "$TYPE" = "admin" ]; then
        # Create README for admins
        create_readme
        tar -cf "${CERT_NAME}.tar" "${CERT_NAME}.p12" "${CERT_NAME}.README"
    else
        # For computers, include crt and key as well
        tar -cf "${CERT_NAME}.tar" "${CERT_NAME}.p12" "${CERT_NAME}.crt" "${CERT_NAME}.key"
    fi
    log_success "Bundle created: ${CERT_NAME}.tar"
}

create_readme() {
    cat <<EOF > "${CERT_NAME}.README"
Wellcome to migasfree, we love change !!!

To access the migasfree console, the use of a mutual TLS (mTLS) certificate is required.
Steps to Import your Personal Digital Certificate (mTLS) in Mozilla Firefox:
1. Open Firefox -> Settings -> Privacy & Security
2. View Certificates -> Your Certificates -> Import
3. Select '${CERT_NAME}.p12' and enter password.
4. Visit https://${HOST}/

EOF
    _issued=$(openssl x509 -in "${CERT_NAME}.crt" -noout -startdate | cut -d= -f2)
    _expiry=$(openssl x509 -in "${CERT_NAME}.crt" -noout -enddate | cut -d= -f2)
    {
        echo "File: ${CERT_NAME}.p12"
        echo "Issue date: $_issued"
        echo "Expiry date: $_expiry"
    } >> "${CERT_NAME}.README"
}

# ============================================================================
# Main
# ============================================================================

main() {
    TYPE="${1:-}"
    FQDN="${2:-}"
    HOST="${3:-}"
    STACK="${4:-}"
    CERT_NAME="${5:-}"
    PASSWORD="${6:-}"
    DAYS_VALID="${7:-$DEFAULT_DAYS_VALID}"
    EMAIL="${8:-}"

    validate_arguments

    PATH_CA="/mnt/cluster/certificates/${STACK}/ca"
    PATH_RESOURCE="/mnt/cluster/certificates/${STACK}/${TYPE}"
    PATH_CERTS="${PATH_RESOURCE}/certs"
    CA_CERT="${PATH_CA}/ca.crt"
    CA_KEY="${PATH_CA}/ca.key"
    CONFIG_EXT="${PATH_CERTS}/${CERT_NAME}.cnf"

    validate_paths
    trap cleanup_temp_files EXIT
    cd "$PATH_CERTS"

    log_info "Starting certificate generation ($TYPE) for: $CERT_NAME"
    create_extension_config
    generate_private_key
    generate_csr
    sign_certificate
    create_pkcs12
    create_tar_bundle

    log_success "Certificate generation completed successfully!"
}

main "$@"

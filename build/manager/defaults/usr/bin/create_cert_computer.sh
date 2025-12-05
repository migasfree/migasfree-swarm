#!/bin/sh
#
# create_cert_computer.sh - Generate mTLS client certificate for migasfree computers
#
# Usage: create_cert_computer.sh FQDN HOST STACK CERT_NAME PASSWORD [DAYS_VALID] [EMAIL]
#
# Arguments:
#   FQDN       - Fully Qualified Domain Name
#   HOST       - Host for the CRL distribution point
#   STACK      - Stack name for certificate paths
#   CERT_NAME  - Certificate name (format: <UUID>_<PROJECT_ID>)
#   PASSWORD   - Password for the private key and PKCS#12 file
#   DAYS_VALID - (Optional) Certificate validity in days (default: 7305 = ~20 years)
#   EMAIL      - (Optional) Email address for the certificate
#

set -e

# ============================================================================
# Configuration
# ============================================================================
SCRIPT_NAME="$(basename "$0")"
DEFAULT_DAYS_VALID="7305"

# ============================================================================
# Functions
# ============================================================================

log_info() {
    echo "[INFO] $*"
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_success() {
    echo "[OK] $*"
}

show_usage() {
    cat <<EOF
Usage: $SCRIPT_NAME FQDN HOST STACK CERT_NAME PASSWORD [DAYS_VALID] [EMAIL]

Arguments:
  FQDN       - Fully Qualified Domain Name
  HOST       - Host for the CRL distribution point
  STACK      - Stack name for certificate paths
  CERT_NAME  - Certificate name (format: <UUID>_<PROJECT_ID>)
  PASSWORD   - Password for the private key
  DAYS_VALID - Certificate validity in days (default: $DEFAULT_DAYS_VALID)
  EMAIL      - Email address for the certificate

Example:
  $SCRIPT_NAME example.com console.example.com mystack D11EDBB7-3C9D-4406-A813-CEB6DD823C87_1 secret123 365 user@example.com
EOF
}

validate_arguments() {
    if [ -z "${FQDN:-}" ]
    then
        log_error "FQDN is required"
        show_usage
        exit 1
    fi

    if [ -z "${HOST:-}" ]
    then
        log_error "HOST is required"
        show_usage
        exit 1
    fi

    if [ -z "${STACK:-}" ]
    then
        log_error "STACK is required"
        show_usage
        exit 1
    fi

    if [ -z "${CERT_NAME:-}" ]
    then
        log_error "CERT_NAME is required"
        show_usage
        exit 1
    fi

    if [ -z "${PASSWORD:-}" ]
    then
        log_error "PASSWORD is required"
        show_usage
        exit 1
    fi
}

validate_paths() {
    if [ ! -d "$PATH_CERTS" ]
    then
        log_error "Certificates directory does not exist: $PATH_CERTS"
        exit 1
    fi

    if [ ! -f "$CA_CERT" ]
    then
        log_error "CA certificate not found: $CA_CERT"
        exit 1
    fi

    if [ ! -f "$CA_KEY" ]
    then
        log_error "CA private key not found: $CA_KEY"
        exit 1
    fi

    if [ ! -f "${PATH_RESOURCE}/openssl.cnf" ]
    then
        log_error "OpenSSL config not found: ${PATH_RESOURCE}/openssl.cnf"
        exit 1
    fi
}

cleanup_temp_files() {
    exit_code=$?
    log_info "Cleaning up temporary files..."

    cd "$PATH_CERTS" 2>/dev/null || true

    # Remove temporary files (POSIX-compatible, no arrays)
    for file in \
        "${CERT_NAME}.p12" \
        "${CERT_NAME}.README" \
        "${CERT_NAME}.key" \
        "${CERT_NAME}.csr" \
        "${CERT_NAME}.cnf"
    do
        [ -f "$file" ] && rm -f "$file"
    done

    if [ $exit_code -ne 0 ]
    then
        # Also remove .crt and .tar on error
        rm -f "${CERT_NAME}.crt" 2>/dev/null || true
        rm -f "${CERT_NAME}.tar" 2>/dev/null || true
        log_error "Certificate generation failed"
    fi

    exit $exit_code
}

create_extension_config() {
    cat > "$CONFIG_EXT" <<EOF
[ v3_ext ]
extendedKeyUsage = clientAuth, 1.2.3.4.5.6.7.8.2
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
        -subj "/emailAddress=${EMAIL}/CN=${CERT_NAME}/OU=COMPUTERS/O=${FQDN}"
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
    tar -cf "${CERT_NAME}.tar" "${CERT_NAME}.p12"
    log_success "Bundle created: ${CERT_NAME}.tar"
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Parse arguments
    FQDN="${1:-}"
    HOST="${2:-}"
    STACK="${3:-}"
    CERT_NAME="${4:-}"
    PASSWORD="${5:-}"
    DAYS_VALID="${6:-$DEFAULT_DAYS_VALID}"
    EMAIL="${7:-}"

    # Validate required arguments
    validate_arguments

    # Setup paths
    readonly PATH_CA="/mnt/cluster/certificates/${STACK}/ca"
    readonly PATH_RESOURCE="/mnt/cluster/certificates/${STACK}/computer"
    readonly PATH_CERTS="/mnt/cluster/certificates/${STACK}/computer/certs"
    readonly CA_CERT="${PATH_CA}/ca.crt"
    readonly CA_KEY="${PATH_CA}/ca.key"
    readonly CONFIG_EXT="${PATH_CERTS}/${CERT_NAME}.cnf"

    # Validate paths exist
    validate_paths

    # Set trap for cleanup on exit (success or failure)
    trap cleanup_temp_files EXIT

    # Change to certificates directory
    cd "$PATH_CERTS"

    log_info "Starting certificate generation for: $CERT_NAME"
    log_info "FQDN: $FQDN | HOST: $HOST | STACK: $STACK"

    # Generate certificate
    create_extension_config
    generate_private_key
    generate_csr
    sign_certificate
    create_pkcs12
    create_tar_bundle

    echo ""
    log_success "Certificate generation completed successfully!"
    log_info "Output file: ${PATH_CERTS}/${CERT_NAME}.tar"
    echo ""
}

# Run main function
main "$@"

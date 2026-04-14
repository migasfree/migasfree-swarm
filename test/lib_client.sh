#!/bin/bash

# Migasfree Test Client Library
# Shared logic for client test environments

STACK_DIR="/stack"
CLUSTER_DIR="/mnt/cluster"

get_swarm_context() {
    if [ -d "$STACK_DIR" ]; then
        # shellcheck source=/dev/null
        source /venv/bin/activate
        FQDN=$(python3 -c "import sys; sys.path.append('$STACK_DIR'); import env; print(env.FQDN)")
        STACK=$(python3 -c "import sys; sys.path.append('$STACK_DIR'); import env; print(env.STACK)")
        EXPORT_CA_SOURCE="$CLUSTER_DIR/certificates/$STACK/ca/ca.crt"
    else
        echo "Error: This script must be run from within the migasfree-swarm context."
        return 1
    fi
}

prepare_ca() {
    local target_dir="defaults/usr/share/ca-certificates"
    if [ -n "$EXPORT_CA_SOURCE" ] && [ -f "$EXPORT_CA_SOURCE" ]; then
        echo "Copying CA certificate from $EXPORT_CA_SOURCE..."
        mkdir -p "$target_dir"
        cp "$EXPORT_CA_SOURCE" "$target_dir/ca.crt"
        return 0
    else
        echo "Warning: CA certificate not found at $EXPORT_CA_SOURCE."
        return 1
    fi
}

# Optional: PEM conversion for certain distributions
convert_ca_to_pem() {
    local ca_file="defaults/usr/share/ca-certificates/ca.crt"
    local pem_file="defaults/usr/share/ca-certificates/ca.pem"
    if [ -f "$ca_file" ]; then
        openssl x509 -in "$ca_file" -out "$pem_file" -outform PEM
    fi
}

build_and_run_client() {
    local image_name="$1"
    local project_name="$2"
    local debug="${3:-False}"
    
    local version
    version=$(cat VERSION)
    
    echo "Building $image_name image version $version..."
    docker build . -t "$image_name:$version"

    echo "Running $image_name container..."
    docker run --rm \
        -e TZ="Europe/Madrid" \
        -e MIGASFREE_CLIENT_SERVER="${FQDN}" \
        -e MIGASFREE_CLIENT_PROJECT="${project_name}" \
        -e MIGASFREE_CLIENT_PROTOCOL=https \
        -e MIGASFREE_CLIENT_DEBUG="${debug}" \
        -e USER=root \
        -ti "$image_name:$version" bash
}

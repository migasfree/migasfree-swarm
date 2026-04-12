#!/bin/sh
set -e

# Try to find the proxy container for the current stack
CONTAINER_PROXY_ID=$(docker ps | grep "${STACK}_proxy" | awk '{print $1}')

if [ -z "$CONTAINER_PROXY_ID" ]; then
    echo "Error: Proxy container for stack '${STACK}' not found."
    exit 1
fi

echo
echo "● portainer:"
echo
docker exec -ti "${CONTAINER_PROXY_ID}" sh -c "printf '    '; cat /var/run/secrets/swarm-credential | tr ':' ' '; echo"
echo

for _DIR in /mnt/cluster/datashares/*; do
    if [ -d "$_DIR" ]; then
        _STACK_NAME=$(basename "$_DIR")
        _ENV_FILE="$_DIR/env.py"
        
        if [ -f "$_ENV_FILE" ]; then
            # Temporarily source to get FQDN for this stack
            # shellcheck source=/dev/null
            . "$_ENV_FILE"
            
            echo "● Stack ${_STACK_NAME}:"

            echo
            echo "    ● database_console:"
            echo
            docker exec -ti "${CONTAINER_PROXY_ID}" sh -c "printf '        '; cat /var/run/secrets/${_STACK_NAME}_superadmin_name; printf '@%s ' '${FQDN}'; cat /var/run/secrets/${_STACK_NAME}_superadmin_pass; echo"

            echo
            echo "    ● Others:"
            echo
            docker exec -ti "${CONTAINER_PROXY_ID}" sh -c "printf '        '; cat /var/run/secrets/${_STACK_NAME}_superadmin_name; printf ' '; cat /var/run/secrets/${_STACK_NAME}_superadmin_pass; echo"
            echo
        fi
    fi
done

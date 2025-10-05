#!/bin/sh

PATH_CA="/mnt/cluster/certificates"
PATH_MTLS="${PATH_CA}/mtls/certs"
CA_CONF="${PATH_CA}/mtls/mtls.cnf"

PATH_DATASHARE="/mnt/cluster/datashares"

STACKS=$(find "${PATH_DATASHARE}" -mindepth 1 -maxdepth 1 -type d)

count=$(echo "${STACKS}" | wc -l)
if [ "$count" -eq 1 ]; then

  STACK=$(basename "${STACKS}")
else
  echo "STACKS found:"
  echo "${STACKS}" | while read -r d; do
    echo "  - $(basename "$d")"
  done
  read -p "STACK to use: " STACK
fi
source ${PATH_DATASHARE}/${STACK}/env.py

read -p "user: " USER

CERTIFICATE="${PATH_MTLS}/${USER}-${FQDN}.crt"

# Revoke certificate
openssl ca -config $CA_CONF -revoke ${CERTIFICATE}

# Update CRL
openssl ca -config $CA_CONF -gencrl -out ${PATH_CA}/mtls/crl.pem

if [ $? = 0 ]
then

  # Delete files
  rm ${PATH_MTLS}/${USER}-${FQDN}*

  # Update CRL & reload all haproxy
  COMMAND="echo -e 'commit ssl crl-file ${PATH_CA}/mtls/crl.pem' | socat stdio tcp4-connect:127.0.0.1:8404"
  CONTAINERS=$(docker service ps --filter "desired-state=running" --format "{{.ID}}" "proxy_proxy")
  for TASK_ID in $CONTAINERS; do
    # Obtener el container ID asociado a la tarea
    CONTAINER_ID=$(docker inspect --format '{{.Status.ContainerStatus.ContainerID}}' "$TASK_ID")
    if [[ -n "$CONTAINER_ID" ]]; then
      docker exec "$CONTAINER_ID" bash -c "$COMMAND"
      docker exec "$CONTAINER_ID" bash -c "reload"
    fi
  done
fi
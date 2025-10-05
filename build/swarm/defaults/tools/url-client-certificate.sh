#!/bin/sh

PATH_DATASHARE="/mnt/cluster/datashares"
PATH_TOKEN=/mnt/cluster/certificates/mtls/token
PATH_CERTS=/mnt/cluster/certificates/mtls/certs

STACKS=$(find "${PATH_DATASHARE}" -mindepth 1 -maxdepth 1 -type d)

mkdir -p ${PATH_TOKEN}

echo

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

if [ -f "${PATH_CERTS}/${USER}-${FQDN}.crt" ]
then
  echo "

    WARNING
    =======
    The user '${USER}' in '${FQDN}' already has an issued client certificate.
    You must revoke the existing certificate before issuing a new one.
    Please execute: ./migasfree-swarm revoke-client-certificate
"
  exit 1

else

    read -p "validity in days (7300):" DAYS

    UUID=$(openssl rand -hex 32)
    FILE="${PATH_TOKEN}/${UUID}"

    echo -n "${USER}|${DAYS}" > ${FILE}
    chmod 400 ${FILE}
    echo
    echo "Please, send this url to ${USER}:"
    echo "    https://${FQDN}/services/mtls?token=${UUID}"
    echo
    exit 0
fi
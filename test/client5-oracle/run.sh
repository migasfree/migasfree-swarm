#!/bin/bash

# shellcheck source=/dev/null
source ../lib_client.sh

get_swarm_context || exit 1
prepare_ca
convert_ca_to_pem
build_and_run_client "migasfree/client-oracle" "fedora"

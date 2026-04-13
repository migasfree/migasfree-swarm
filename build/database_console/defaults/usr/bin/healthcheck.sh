#!/bin/sh
. /usr/bin/common.sh
check_http "http://localhost:${PGADMIN_LISTEN_PORT}/misc/ping"

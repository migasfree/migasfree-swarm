#!/bin/sh
. /usr/bin/common.sh
check_http http://127.0.0.1:8080/manager/v1/internal/health

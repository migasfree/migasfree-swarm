#!/bin/sh
# TDA healthcheck: verify the web server is responsive and output dir is writable
if [ -d "/data/tda" ] && [ -w "/data/tda" ]; then
    curl -s -f http://127.0.0.1:8000/api/v1/health > /dev/null 2>&1
    exit $?
fi
exit 1


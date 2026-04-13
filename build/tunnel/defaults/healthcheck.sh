#!/bin/bash

. /usr/bin/common.sh

if ! check_tcp localhost 8080
then
    echo "WebSocket port 8080 not listening"
    exit 1
fi

if ! check_tcp datastore 6379
then
    echo "Redis datastore:6379 not reachable"
    exit 1
fi

if [ "$(ulimit -n)" -lt 5000 ]
then
    echo "File descriptor limit too low: $(ulimit -n)"
fi

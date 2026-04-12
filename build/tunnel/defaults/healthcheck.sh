#!/bin/sh
set -e

if ! nc -z localhost 8080 > /dev/null 2>&1
then
    echo "WebSocket port 8080 not listening"
    exit 1
fi

if ! nc -z datastore 6379 > /dev/null 2>&1
then
    echo "Redis datastore:6379 not reachable"
    exit 1
fi

if [ "$(ulimit -n)" -lt 5000 ]
then
    echo "File descriptor limit too low: $(ulimit -n)"
fi

exit 0

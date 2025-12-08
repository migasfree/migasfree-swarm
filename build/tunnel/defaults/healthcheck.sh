#!/bin/sh

if ! timeout 3 bash -c "echo > /dev/tcp/localhost/8080" 2>/dev/null; then
    echo "❌ WebSocket port 8080 not listening"
    exit 1
fi

if ! timeout 3 bash -c "echo > /dev/tcp/datastore/6379" 2>/dev/null; then
    echo "❌ Redis datastore:6379 not reachable"
    exit 1
fi

if [ "$(ulimit -n)" -lt 5000 ]; then
    echo "⚠️  File descriptor limit too low: $(ulimit -n)"
fi


exit 0
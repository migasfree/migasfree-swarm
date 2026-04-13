#!/bin/sh
. /usr/bin/common.sh
# Check HTTPS with -k (insecure) because it's localhost and might have self-signed or internal CA
curl -sfk --max-time 3 https://localhost:8404/health > /dev/null 2>&1

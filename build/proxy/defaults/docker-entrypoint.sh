#!/bin/sh
set -e

. /usr/bin/common.sh
set_tz

if ! [ -f /mnt/cluster/certificates/inv/ca/ca.crt ]
then
    wait_for_service "manager" "8080"
fi

cd /usr/share/proxy || exit 1

# shellcheck source=/dev/null
. /venv/bin/activate

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]
then
    set -- haproxy "$@"
fi

start_message

show_banner "$(haproxy -v | head -n 1)"

# load proxy
# =============
mkdir -p /var/run/haproxy/

# Certificates
rm -rf /usr/local/etc/haproxy/certificates || :
ln -snf /mnt/cluster/certificates /usr/local/etc/haproxy/certificates

cd /usr/share/proxy || exit 1
python3 init.py
cd - > /dev/null

send_message ""

exec haproxy -W -db -S /var/run/haproxy/haproxy-master-socket -f /etc/haproxy/haproxy.cfg \
    -p /var/run/haproxy/haproxy.pid -4

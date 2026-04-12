#!/bin/sh
set -e

# Set Timezone
if [ -n "$TZ" ] && [ -f "/usr/share/zoneinfo/$TZ" ]
then
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "$TZ" > /etc/timezone
fi

wait() {
    _SERVER=$1
    _PORT=$2
    _COUNTER=0

    until [ "$_COUNTER" -gt 30 ]
    do
        if nc -z "$_SERVER" "$_PORT" 2> /dev/null
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        _COUNTER=$((_COUNTER + 1))
    done
    echo "Rebooting container"
    exit 1
}

if ! [ -f /mnt/cluster/certificates/inv/ca/ca.crt ]
then
    wait "manager" "8080"
fi

cd /usr/share/proxy || exit 1

# shellcheck source=/dev/null
. /venv/bin/activate

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]
then
    set -- haproxy "$@"
fi

send_message "Initial configuration"

echo "


                   █                          ██
                                             █
         ███ ██    █    ██     ███     ███  ████  ███  ███    ███
        █   █  █   █   █  █       █   █      █   █    █   █  █   █
        █   █  █   █   █  █    ████    ██    █   █    ████   ████
        █   █  █   █   █  █   █   █      █   █   █    █      █
        █   █  █   █    ███    ███    ███    █   █     ███    ███
                          █
        we love change  ██


        $SERVICE ($TAG)
        $(haproxy -v | head -n 1)
        Container: $(hostname)
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

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

#!/bin/bash

set -e

function wait {
    local _SERVER=$1
    local _PORT=$2
    local _COUNTER=0

    until [ $_COUNTER -gt 30 ]
    do
        if nc -z "$_SERVER" "$_PORT" 2> /dev/null
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        ((_COUNTER++))
    done
    echo "Rebooting container"
    exit 1
}


if ! [ -f /mnt/cluster/certificates/inv/ca/ca.crt ]
then
    wait "ca" "8080"
fi

. /venv/bin/activate


# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]
then
    set -- haproxy "$@"
fi


# services page
# =============
cd /usr/share/services/
python3 services.py 8001 &
cd -

send_message "Initial configuration" "localhost"

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
        $(haproxy -v | head -1)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

# load proxy
# =============
mkdir -p /var/run/haproxy/


# Certificates
rm -rf /usr/local/etc/haproxy/certificates || :
ln -s /mnt/cluster/certificates /usr/local/etc/haproxy/certificates

send_message "" "localhost"

haproxy -W -db -S /var/run/haproxy/haproxy-master-socket -f /etc/haproxy/haproxy.cfg \
    -p /var/run/haproxy/haproxy.pid -4

#!/bin/sh

wait_for_dns "proxy"

send_message "Starting Certificate Authority"

/usr/bin/create_local_ca.sh ${STACK}

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
        Uvicorn: $(uvicorn --version)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

/usr/sbin/crond &
/usr/bin/renew_crl

send_message ""

uvicorn main:app --host "0.0.0.0" --port 80 --log-level info

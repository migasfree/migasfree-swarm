#!/bin/bash

send_message "init mcp-server"

sudo update-ca-certificates

cd /app

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
        $(pip freeze|grep mcp)
        Container: $HOSTNAME
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

send_message ""

python server.py

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
        mcp-server
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

send_message ""

mcpo --port 8080 -- python server.py

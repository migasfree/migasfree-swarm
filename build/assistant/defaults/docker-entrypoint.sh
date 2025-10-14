#!/bin/bash

wait_for_dns "proxy"

cd /app/backend

send_message "Starting assistant"
init-assistant &

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
        Webui build version: $WEBUI_BUILD_VERSION
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"


send_message ""
bash start.sh

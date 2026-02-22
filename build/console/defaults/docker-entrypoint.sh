#!/bin/bash

# Set Timezone
if [ -n "$TZ" ] && [ -f "/usr/share/zoneinfo/$TZ" ]; then
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "$TZ" > /etc/timezone
fi

function wait {
    local _SERVER=$1
    local _PORT=$2
    local _COUNTER=0
    until [ $_COUNTER -gt 30 ]
    do
        nc -z $_SERVER $_PORT 2> /dev/null
        if [ $? = 0 ]
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        _COUNTER=$(( $_COUNTER + 1 ))
    done
    echo "Rebooting container"
    exit 1
}

# Configure ngnix
cat << EOF > /etc/nginx/conf.d/default.conf
server {
    listen       80;
    server_name  localhost 127.0.0.1 console $(hostname);

    access_log  /dev/stdout  main;
    error_log /dev/stderr warn;

    # mode history: https://router.vuejs.org/guide/essentials/history-mode.html#example-server-configurations
    location / {
        root   /usr/share/nginx/html;
        try_files \$uri \$uri/ /index.html;
    }

    location /index.html {
        # /index.html no cache
        root /usr/share/nginx/html;
        add_header Cache-Control "private, no-cache, no-store, must-revalidate";
        add_header Expires "Sat, 01 Jan 2000 00:00:00 GMT";
        add_header Pragma no-cache;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
EOF

send_message "starting ${SERVICE:(${#STACK})+1}"

# Hacking enviroment variable MIGASFREE_SERVER for production
_FILES=$(grep -l __FQDN__ /usr/share/nginx/html/js/*)
for _FILE in $_FILES
do
    sed -i "s/__FQDN__/$FQDN/g" $_FILE
done

send_message "waiting core"
wait core 8080

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
        $(nginx -v 2>&1)
        Container: $HOSTNAME
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

echo "daemon off;" >> /etc/nginx/nginx.conf

send_message ""
nginx

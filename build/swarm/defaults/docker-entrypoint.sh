#!/bin/sh

function set_TZ {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime || :
}


set_TZ

COMMAND="$1"

cp /tools/migasfree-swarm /stack/migasfree-swarm

. /venv/bin/activate

if [ -z ${COMMAND} ]
then
    echo "
        $SERVICE ($TAG)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)"
    echo
    # TODO install plugin S3
    # python3 /usr/bin/install-plugin

elif [ ${COMMAND} = "deploy" ]
then
    python3 /tools/deploy.py

elif [ ${COMMAND} = "undeploy" ]
then
    python3 /tools/undeploy.py

elif [ ${COMMAND} = "consoles-dev" ]
then
    python3 /tools/consoles.py "dev"

elif [ ${COMMAND} = "consoles-pro" ]
then
    python3 /tools/consoles.py "pro"

elif [ ${COMMAND} = "secret" ]
then
    /tools/secret.sh

elif [ ${COMMAND} = "config" ]
then
    python3 /tools/config.py

elif [ ${COMMAND} = "config-stack" ]
then
    python3 /tools/config-stack.py

elif [ ${COMMAND} = "leave" ]
then
    python3 /tools/leave.py

elif [ ${COMMAND} = "pull" ]
then
    /tools/pull.sh

elif [ ${COMMAND} = "join-worker" ]
then
    /tools/join-worker.sh

fi

rm -rf /stack/__pycache__  || :
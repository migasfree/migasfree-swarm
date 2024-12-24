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

function get_swarm_role() {
    if ! docker info | grep -q "Swarm: active"; then
        echo ""
    else
      if docker info | grep -q "Is Manager: true"; then
          echo "MANAGER"
      else
          echo "WORKER"
      fi
    fi
}


function run_manager() {
    local _COMMAND="$1"
    local _SILENT="$2"
    if [ -z ${ROLE}  ]
    then
        echo "This host is not part of a Swarm cluster."
        exit 1
    fi
    if [ ${ROLE} = "MANAGER" ]
    then
        $_COMMAND
    else
        if ! [ "${_SILENT}" = "silent" ]
        then
            echo "This node is a Swarm worker."
            echo "This command is only executable on a Swarm manager node."
        fi
    fi
}

set_TZ

COMMAND="$1"
ROLE="$(get_swarm_role)"

if [ -d /stack ]
then
    cp /tools/migasfree-swarm /stack/migasfree-swarm
fi
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
    run_manager "python3 /tools/undeploy.py"

elif [ ${COMMAND} = "consoles-dev" ]
then
    run_manager "python3 /tools/consoles.py 'dev'"

elif [ ${COMMAND} = "consoles-pro" ]
then
    run_manager "python3 /tools/consoles.py 'pro'"

elif [ ${COMMAND} = "secret" ]
then
    run_manager "/tools/secret.sh"

elif [ ${COMMAND} = "config" ]
then
    python3 /tools/config.py

elif [ ${COMMAND} = "config-stack" ]
then
    run_manager "python3 /tools/config-stack.py"

elif [ ${COMMAND} = "leave" ]
then
    run_manager "python3 /tools/leave.py"

elif [ ${COMMAND} = "pull" ]
then
    /tools/pull.sh

elif [ ${COMMAND} = "join-worker" ]
then
    run_manager "/tools/join-worker.sh"
else
    echo "Unknown command: ${COMMAND}"
fi

rm -rf /stack/__pycache__  || :
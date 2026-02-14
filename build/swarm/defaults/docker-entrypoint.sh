#!/bin/sh

set_TZ() {
    : ${TZ:=Europe/Madrid}
    # Link only if the target differs (reduces noisy “File exists” errors)
    [ "$(readlink /etc/localtime)" != "/usr/share/zoneinfo/$TZ" ] && \
        ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime
}

get_swarm_role() {
    local info

    info=$(docker info 2>/dev/null) || { echo ""; return; }
    echo "$info" | grep -q "Swarm: active" || { echo ""; return; }
    echo "$info" | grep -q "Is Manager: true" && echo "MANAGER" || echo "WORKER"
}


run_manager() {
    local _COMMAND="$1"
    local _SILENT="${2:-}"
    if [ -z "${ROLE}" ]
    then
        echo "This host is not part of a Swarm cluster."
        exit 1
    fi
    if [ "${ROLE}" = "MANAGER" ]
    then
        $_COMMAND
    elif [ "${_SILENT}" != "silent" ]
    then
        echo "This node is a Swarm worker."
        echo "This command is only executable on a Swarm manager node."
    fi
}

show_help() {
    cat <<EOF
Usage:
  migasfree-swarm <command>

Available commands:
  deploy                 Deploy a migasfree stack
  undeploy               Undeploy a migasfree stack
  redeploy               Perform undeploy + deploy
  deploy-all             Deploy all migasfree stacks
  undeploy-all           Undeploy all migasfree stacks
  redeploy-all           Perform undeploy + deploy for all migasfree stacks
  consoles-dev           Enable development consoles
  consoles-pro           Disable development consoles
  secret                 Show the "secrets" for console access
  config                 Configure the swarm cluster
  pull                   Pull all images
  url-admin-certificate  Generate a one-time URL to create a client certificate for administration console access
  join-worker            Add a worker node to the cluster
EOF
}

set_TZ

COMMAND="$1"
ROLE="$(get_swarm_role)"

[ -d /stack ] && cp /tools/migasfree-swarm /stack/migasfree-swarm
. /venv/bin/activate

case "$COMMAND" in
    deploy)
        python3 /tools/deploy.py
    ;;

    undeploy)
        run_manager "python3 /tools/undeploy.py"
    ;;

    redeploy)
        run_manager "python3 /tools/undeploy.py"
        python3 /tools/deploy.py
    ;;

    deploy-all|deploy_all)
        run_manager "/tools/deploy_all.sh"
    ;;

    undeploy-all|undeploy_all)
        run_manager "/tools/undeploy_all.sh"
    ;;

    redeploy-all|redeploy_all)
        run_manager "/tools/undeploy_all.sh"
        run_manager "/tools/deploy_all.sh"
    ;;

    consoles-dev|consoles_dev)
        run_manager "python3 /tools/consoles.py 'dev'"
    ;;

    consoles-pro|consoles_pro)
        run_manager "python3 /tools/consoles.py 'pro'"
    ;;

    secret|secrets)
        run_manager "/tools/secret.sh"
    ;;

    config)
        python3 /tools/config.py
    ;;

    config-stack|config_stack)
        run_manager "python3 /tools/config-stack.py"
    ;;

    leave)
        run_manager "python3 /tools/leave.py"
    ;;

    pull)
        /tools/pull.sh
    ;;

    url-admin-certificate|url_admin_certificate)
        run_manager "python3 /tools/url-admin-certificate.py"
    ;;

    join-worker|join_worker)
        run_manager "/tools/join-worker.sh"
    ;;

    *)
        echo "
            $SERVICE ($TAG)
            Container: $HOSTNAME
            Time zome: $TZ $(date)
            Processes: $(nproc)"
        echo
        show_help

    ;;
esac

rm -rf /stack/__pycache__  || :

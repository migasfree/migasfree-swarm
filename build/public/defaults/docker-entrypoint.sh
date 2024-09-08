function set_TZ {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime || :
}

function wait {
    local _SERVER=$1
    local _PORT=$2
    local _COUNTER=0

    until [ $_COUNTER -gt 30 ]
    do
        nc -z $_SERVER $_PORT 2> /dev/null
        if [ $? -eq 0 ]
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

send_message "starting ${SERVICE:(${#STACK})+1}"

set_TZ

export MIGASFREE_CONF_DIR=/var/lib/migasfree-backend/conf
mkdir -p $(dirname ${MIGASFREE_CONF_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/conf ${MIGASFREE_CONF_DIR}

export MIGASFREE_PUBLIC_DIR=/var/migasfree/public
mkdir -p $(dirname ${MIGASFREE_PUBLIC_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/public ${MIGASFREE_PUBLIC_DIR}

export MIGASFREE_POOL_DIR=/var/migasfree/pool
mkdir -p $(dirname ${MIGASFREE_POOL_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/pool ${MIGASFREE_POOL_DIR}

_CONTAINER=$(hostname)
sed -i "s/@container@/$_CONTAINER/g" /var/migasfree/404.html
sed -i "s/@container@/$_CONTAINER/g" /var/migasfree/50x.html

# TODO: Remove link. Warning!!! Afect to symbolic links of packages in REPOSITORIES.
# ¿Changes MIGASFREE_PUBLIC_DIR = '/var/migasfree/repo' in source?
ln -s /var/migasfree/public /var/migasfree/repo

send_message "waiting core"
wait core 8080

echo "


                   ●                          ●●
                                             ●
         ●●● ●●    ●    ●●     ●●●     ●●●  ●●●●  ●●●  ●●●    ●●● 
        ●   ●  ●   ●   ●  ●       ●   ●      ●   ●    ●   ●  ●   ●
        ●   ●  ●   ●   ●  ●    ●●●●    ●●    ●   ●    ●●●●   ●●●● 
        ●   ●  ●   ●   ●  ●   ●   ●      ●   ●   ●    ●      ●
        ●   ●  ●   ●    ●●●    ●●●    ●●●    ●   ●     ●●●    ●●●
                          ●
                        ●●


        migasfree PUBLIC
        $(nginx -v 2>&1)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"



reload_proxy

# Get external deployments extensions from proxy
# =================================================
echo "$(curl http://proxy:8001/services/nginx_extensions 2>/dev/null)" > /var/tmp/external-deployments.conf

send_message ""

nginx -g 'daemon off;'

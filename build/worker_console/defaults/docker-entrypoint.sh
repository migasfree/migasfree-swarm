#!/bin/sh

export MIGASFREE_SECRET_DIR=/var/run/secrets
BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0
BACKEND_URL=$BROKER_URL


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
        if [ $? = 0 ]
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

function send_message {
    local _POINT="http://proxy:8001/services/message"
    local _DATA="{ \"text\":\"$1\", \"service\":\"$SERVICE\" ,\"node\":\"$NODE\",\"container\":\"$HOSTNAME\" }"

    until [ $(curl -s -o /dev/null  -w '%{http_code}' -d "$_DATA" -H "Content-Type: application/json" -X POST $_POINT) = "200" ]
    do
        sleep 2
    done
}

function reload_proxy {
    curl -d "" -X POST http://proxy:8001/services/reconfigure &> /dev/null
}



send_message "init worker console"
send_message "wait worker"

#wait worker 8080

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

        migasfree worker console
        celery $(celery --version)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

reload_proxy


# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
echo "broker_url = '${BROKER_URL}'" > ${CONFIG_FILE}
echo "result_backend = '${BROKER_URL}'"  >> ${CONFIG_FILE}
echo "broker_connection_retry_on_startup = True" >> ${CONFIG_FILE}
echo "enable_utc = False" >> ${CONFIG_FILE}
echo "timezone = '${TZ}'" >> ${CONFIG_FILE}


send_message ""

export FLOWER_UNAUTHENTICATED_API=True 
#export FLOWER_BASIC_AUTH=default:oh4zd_JKphLw7AWwE_lJ
celery --config celeryconfig flower --persistent=True --state_save_interval=15000 --db="/data/flower" --broker-api=${BROKER_URL}/api/ 
#--basic-auth=admin:oh4zd_JKphLw7AWwE_lJ

export MIGASFREE_FQDN=core:8080
export MIGASFREE_SECRET_DIR=/var/run/secrets

QUEUES="pms-pacman"
BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0
BACKEND_URL=$BROKER_URL
export CELERY_BROKER_URL=${BROKER_URL}


function wait {
    local _SERVER=$1
    local _PORT=$2
    local counter=0
    until [ $counter -gt 30 ]
    do
        nc -z $_SERVER $_PORT 2> /dev/null
        if [ $? = 0 ]
        then
            echo "$_SERVER:$_PORT is running."
            return
        else
            echo "$_SERVER:$_PORT is not running after $counter seconds."
            sleep 1
        fi
        ((counter++))
    done
    echo "Rebooting container"
    exit 1
}

function default_pms_pass {
    local IS_DEFAULT=$(curl -w "%{http_code}" --insecure -o /var/tmp/token_pms -H "Content-Type: application/json" -X POST --data '{"username":"pms","password":"pms"}' http://core:8080/token-auth/  2> /dev/null) 
    if [ "${IS_DEFAULT}" = "200" ]
    then
        # Change password to user pms
        local TOKEN_DEFAULT=$(cat /var/tmp/token_pms | awk -F "\"" '{print $4}')
        local NEW_PASSWORD=$(cat /run/secrets/${STACK}_pms_pass)
        curl --insecure -X POST -H "Content-Type: application/json" -H "Authorization: Token ${TOKEN_DEFAULT}" -d '{"new_password1": "'${NEW_PASSWORD}'","new_password2":"'${NEW_PASSWORD}'"}' http://core:8080/rest-auth/password/change/   
    fi
    rm /var/tmp/token_pms 
}

function save_token_pms {
    default_pms_pass
    curl --insecure -H "Content-Type: application/json" -X POST --data '{"username":"pms","password":"'$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_pms_pass)'"}' http://core:8080/token-auth/ 2>/dev/null | awk -F "\"" '{print $4}' > ${MIGASFREE_SECRET_DIR}/token_pms 
}


send_message "starting ${SERVICE:(${#STACK})+1}"

export MIGASFREE_KEYS_DIR=/var/lib/migasfree-backend/keys
mkdir -p $(dirname ${MIGASFREE_KEYS_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/keys ${MIGASFREE_KEYS_DIR}

export MIGASFREE_PUBLIC_DIR=/var/lib/migasfree-backend/public
mkdir -p $(dirname ${MIGASFREE_PUBLIC_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/public ${MIGASFREE_PUBLIC_DIR}

export MIGASFREE_TMP_DIR=/var/lib/migasfree-backend/tmp
mkdir -p $(dirname ${MIGASFREE_TMP_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/tmp ${MIGASFREE_TMP_DIR}

export MIGASFREE_CERTIFICATES_DIR=/var/lib/migasfree-backend/certificates
mkdir -p $(dirname ${MIGASFREE_CERTIFICATES_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/certificates ${MIGASFREE_CERTIFICATES_DIR}

export MIGASFREE_PLUGINS_DIR=/pms/migasfree/core/pms/plugins
mkdir -p $(dirname ${MIGASFREE_PLUGINS_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/plugins ${MIGASFREE_PLUGINS_DIR}

export MIGASFREE_STORE_TRAILING_PATH=stores
export MIGASFREE_REPOSITORY_TRAILING_PATH=repos
export MIGASFREE_EXTERNAL_TRAILING_PATH=external
export MIGASFREE_TMP_TRAILING_PATH=tmp

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

        $SERVICE ($TAG)
        celery $(celery --version)
        Container: $HOSTNAME
        Time zome: $TZ  $(date)
        Processes: $(nproc)

"

save_token_pms
cd /pms
reload_proxy


# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
echo "broker_url = '${BROKER_URL}'" > ${CONFIG_FILE}
echo "result_backend = '${BROKER_URL}'"  >> ${CONFIG_FILE}
echo "imports = ('migasfree.core.pms.tasks',)" >> ${CONFIG_FILE}
echo "broker_connection_retry_on_startup = True" >> ${CONFIG_FILE}
echo "worker_concurrency = 3" >> ${CONFIG_FILE}



send_message ""
celery --config celeryconfig worker -l INFO --uid=890 -Q $QUEUES 


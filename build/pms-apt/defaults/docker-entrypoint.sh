export MIGASFREE_FQDN=core:8080
export MIGASFREE_SECRET_DIR=/var/run/secrets

QUEUES="pms-apt"
BROKER_URL=redis://default:$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")@datastore:6379/0
export CELERY_BROKER_URL=${BROKER_URL}

function wait {
    local _SERVER=$1
    local _PORT=$2
    local _COUNTER=0
    until [ $_COUNTER -gt 30 ]
    do
        if nc -z "$_SERVER" "$_PORT" 2> /dev/null
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

function default_pms_pass {
    local IS_DEFAULT
    local TOKEN_DEFAULT
    local NEW_PASSWORD

    IS_DEFAULT=$(
        curl -w "%{http_code}" --insecure -o /var/tmp/token_pms \
            -H "Content-Type: application/json" -X POST \
            --data '{"username":"pms","password":"pms"}' \
            http://${MIGASFREE_FQDN}/token-auth/ 2> /dev/null
    )
    if [ "${IS_DEFAULT}" = "200" ]
    then
        # Change password to user pms
        TOKEN_DEFAULT=$(awk -F "\"" '{print $4}' /var/tmp/token_pms)
        NEW_PASSWORD=$(cat "/run/secrets/${STACK}_pms_pass")
        curl --insecure -X POST -H "Content-Type: application/json" \
            -H "Authorization: Token ${TOKEN_DEFAULT}" \
            -d '{"new_password1": "'${NEW_PASSWORD}'","new_password2":"'${NEW_PASSWORD}'"}' \
            http://${MIGASFREE_FQDN}/rest-auth/password/change/
    fi
    rm /var/tmp/token_pms
}

function save_token_pms {
    default_pms_pass
    curl --insecure -H "Content-Type: application/json" -X POST \
        --data '{"username":"pms","password":"'$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_pms_pass)'"}' \
        http://${MIGASFREE_FQDN}/token-auth/ \
        2>/dev/null | awk -F "\"" '{print $4}' > ${MIGASFREE_SECRET_DIR}/token_pms
}

send_message "starting ${SERVICE:(${#STACK})+1}"

export MIGASFREE_KEYS_DIR=/var/lib/migasfree-backend/keys
mkdir -p "$(dirname ${MIGASFREE_KEYS_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/keys" ${MIGASFREE_KEYS_DIR}

export MIGASFREE_PUBLIC_DIR=/var/lib/migasfree-backend/public
mkdir -p "$(dirname ${MIGASFREE_PUBLIC_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/public" ${MIGASFREE_PUBLIC_DIR}

export MIGASFREE_TMP_DIR=/var/lib/migasfree-backend/tmp
mkdir -p "$(dirname ${MIGASFREE_TMP_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/tmp" ${MIGASFREE_TMP_DIR}

export MIGASFREE_CERTIFICATES_DIR=/var/lib/migasfree-backend/certificates
mkdir -p "$(dirname ${MIGASFREE_CERTIFICATES_DIR})"
ln -s "${DATASHARE_MOUNT_PATH}/certificates" ${MIGASFREE_CERTIFICATES_DIR}

export MIGASFREE_STORE_TRAILING_PATH=stores
export MIGASFREE_REPOSITORY_TRAILING_PATH=repos
export MIGASFREE_EXTERNAL_TRAILING_PATH=external
export MIGASFREE_TMP_TRAILING_PATH=tmp

send_message "waiting ${MIGASFREE_FQDN%:*}"
wait "${MIGASFREE_FQDN%:*}" "${MIGASFREE_FQDN#*:}"

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
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

save_token_pms
cd /pms
reload_proxy


# CELERY CONFIG
# =============
CONFIG_FILE=celeryconfig.py
echo "broker_url = '${BROKER_URL}'" > ${CONFIG_FILE}
echo "result_backend = '${BROKER_URL}'" >> ${CONFIG_FILE}
echo "imports = ('migasfree.core.pms.tasks',)" >> ${CONFIG_FILE}
echo "broker_connection_retry_on_startup = True" >> ${CONFIG_FILE}
echo "worker_concurrency = 3" >> ${CONFIG_FILE}

send_message ""
celery --config celeryconfig worker -l INFO --uid=890 -Q $QUEUES

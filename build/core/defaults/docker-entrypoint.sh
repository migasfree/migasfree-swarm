#!/bin/bash

export MIGASFREE_SECRET_DIR=/var/run/secrets

_SETTINGS=/var/lib/migasfree-backend/conf/settings.py

QUEUES="default"
BROKER_URL=redis://default:$(cat ${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass)@datastore:6379/0
BACKEND_URL=$BROKER_URL
export CELERY_BROKER_URL=${BROKER_URL}


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

function set_TZ {
    # send_message "setting the time zone"
    if [ -z "$TZ" ]
    then
        TZ="Europe/Madrid"
    fi
    # /etc/timezone for TZ setting
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime || :
}

function update_ca_certificates {
    send_message "updating the certificates"
    update-ca-certificates
}

function get_migasfree_setting() {
    echo -n $(DJANGO_SETTINGS_MODULE=migasfree.settings.production python3 -c "from django.conf import settings; print(settings.$1)")
}

function ncores {
    LANG=C lscpu|grep '^Core(s) per socket'| awk -F: '{print $2}'| tr -d  " "
}

# owner resource user
function owner() {
    if [ ! -f "$1" -a ! -d "$1" ]
    then
        mkdir -p "$1"
    fi

    _OWNER=$(stat -c %U "$1" 2> /dev/null)
    if [ "$_OWNER" != "$2" ]
    then
        chown -R $2:$2 "$1"
    fi
}

function get_settings {
    send_message "reading settings"
    if ! [ -f "$_SETTINGS" ]
    then
        cp /default_settings.py $_SETTINGS
    fi
    _HOST=$(get_migasfree_setting "DATABASES['default']['HOST']")
    _PORT=$(get_migasfree_setting "DATABASES['default']['PORT']")
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    _PASSWORD=$(get_migasfree_setting "DATABASES['default']['PASSWORD']")
}

function set_permissions() {
    send_message "setting permissions"
    local _USER=www-data

    # owner for repositories
    local _PUBLIC_PATH=$(get_migasfree_setting MIGASFREE_PUBLIC_DIR)
    owner $_PUBLIC_PATH $_USER

    # owner for keys
    local _KEYS_PATH=$(get_migasfree_setting MIGASFREE_KEYS_DIR)
    owner $_KEYS_PATH $_USER
    chmod 700 $_KEYS_PATH

}

function run_as_www_data {
    su www-data -s /bin/bash -c "$1"
}

#function create_keys {
#    send_message "checking keys"
#    run_as_www_data 'export GPG_TTY=$(tty);DJANGO_SETTINGS_MODULE=migasfree.settings.production python3 -c "import django; django.setup(); from migasfree.secure import create_server_keys; create_server_keys()"'
#}

function is_db_empty() {
    send_message "checking database is empty"
    local _RET=$(PGPASSWORD=$_PASSWORD psql -h $_HOST -p $_PORT -U $_USER $_NAME -tAc "SELECT count(*) FROM information_schema.tables WHERE table_type='BASE TABLE' and table_schema='$_NAME ' ; ")
    test $_RET -eq "$(echo "0")"
}

function is_db_exists() {
    send_message "checking is exists database"
    PGPASSWORD=$_PASSWORD psql -h $_HOST -p $_PORT -U $_USER -tAc "SELECT 1 from pg_database WHERE datname='$_NAME'" 2> /dev/null | grep -q 1
    test $? -eq 0
}

function is_user_exists() {
    send_message "checking user exists in database"
    PGPASSWORD=$_PASSWORD psql -h $_HOST -p $_PORT -U $_USER -tAc "SELECT 1 FROM pg_roles WHERE rolname='$_USER';" | grep -q 1
    test $? -eq 0
}

function create_user() {
    send_message "creating user in database"
    PGPASSWORD=$_PASSWORD psql -h $_HOST -p $_PORT -U $_USER -tAc "CREATE USER $_USER WITH CREATEDB ENCRYPTED PASSWORD '$_PASSWORD';"
    test $? -eq 0
}

function create_database() {
    send_message "creating database"
    PGPASSWORD=$_PASSWORD psql -h $_HOST -p $_PORT -U $_USER -tAc "CREATE DATABASE $_NAME WITH OWNER = $_USER ENCODING='UTF8';"
    test $? -eq 0
}

function migrate {
    send_message "running database migrations"
    su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin migrate auth" www-data
    if [ "$1" = "fake-initial" ]
    then
        su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin migrate --fake-initial" www-data
    else
        su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin migrate" www-data
    fi
}

function apply_fixtures {
    send_message "applying fixtures to database"
    python3 - << EOF
import django
django.setup()

from migasfree.fixtures import create_initial_data, sequence_reset

create_initial_data()
sequence_reset()
EOF
}


function migasfree_init {
    set_permissions

    is_db_exists || create_database

    is_user_exists || create_user

    is_db_empty && echo yes | cat - | migrate "fake-initial" || (
        su -c "django-admin showmigrations | grep '\[ \]' " www-data >/dev/null
        if [ $? -eq 0 ] # we have pending migrations
        then
            migrate
            apply_fixtures
        fi
    )

}


# START
# =====

export MIGASFREE_CONF_DIR=/var/lib/migasfree-backend/conf
mkdir -p $(dirname ${MIGASFREE_CONF_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/conf ${MIGASFREE_CONF_DIR}

export MIGASFREE_PUBLIC_DIR=/var/lib/migasfree-backend/public
mkdir -p $(dirname ${MIGASFREE_PUBLIC_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/public ${MIGASFREE_PUBLIC_DIR}

export MIGASFREE_KEYS_DIR=/var/lib/migasfree-backend/keys
mkdir -p $(dirname ${MIGASFREE_KEYS_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/keys ${MIGASFREE_KEYS_DIR}

export MIGASFREE_TMP_DIR=/var/lib/migasfree-backend/tmp
mkdir -p $(dirname ${MIGASFREE_TMP_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/tmp ${MIGASFREE_TMP_DIR}

export MIGASFREE_PLUGINS_DIR=/venv/lib/python3.11/site-packages/migasfree_backend-$(cat /VERSION)-py3.11.egg/migasfree/core/pms/plugins

cp -r ${DATASHARE_MOUNT_PATH}/plugins/* ${MIGASFREE_PLUGINS_DIR}

. /venv/bin/activate

send_message "waiting datastore"
wait $REDIS_HOST $REDIS_PORT

send_message "waiting database"
wait $POSTGRES_HOST $POSTGRES_PORT

send_message "starting ${SERVICE:(${#STACK})+1}"
set_TZ

if [ "$SERVICE" = "${STACK}_core" ]
then
    get_settings

    update_ca_certificates

    migasfree_init

    _PROCESS=$(pip freeze | grep daphne)
else
    _PROCESS=$(pip freeze | grep celery)
fi

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

        migasfree $SERVICE
        $_PROCESS
        Container: $HOSTNAME
        Time zome: $TZ $(date)

"

reload_proxy
send_message ""

if [ "$SERVICE" = "${STACK}_beat" ]
then
    # BEAT
    DJANGO_SETTINGS_MODULE=migasfree.settings.production celery -A migasfree beat --uid=890 --pidfile /var/tmp/celery.pid --schedule /var/tmp/celerybeat-schedule --loglevel INFO
elif [ "$SERVICE" = "${STACK}_worker" ]
then
    # WORKER
    /usr/bin/migrate_db &
    DJANGO_SETTINGS_MODULE=migasfree.settings.production celery -A migasfree worker --queues=${QUEUES} --uid 890 --without-gossip --loglevel INFO
else
    # CORE
    su -c "uvicorn migasfree.asgi:application --lifespan off --host 0.0.0.0 --port 8080 --workers $((2* $(ncores) + 1 ))" www-data
fi

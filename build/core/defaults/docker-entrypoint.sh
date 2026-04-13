#!/bin/sh
set -e

. /usr/bin/common.sh
export MIGASFREE_SECRET_DIR=/var/run/secrets

_SETTINGS=/var/lib/migasfree-backend/conf/settings.py

QUEUES="default"
load_secret "${STACK}_superadmin_pass" "SUPERADMIN_PASS"
BROKER_URL="redis://default:${SUPERADMIN_PASS}@datastore:6379/0"
export CELERY_BROKER_URL="${BROKER_URL}"

get_secret_pass() {
    echo "$SUPERADMIN_PASS"
}

update_ca_certificates_action() {
    send_message "updating the certificates"
    update-ca-certificates
}

get_migasfree_setting() {
    DJANGO_SETTINGS_MODULE=migasfree.settings.production python3 -c "from django.conf import settings; print(settings.$1)"
}

ncores() {
    _CORES=$(lscpu | grep '^Core(s) per socket' | awk -F: '{print $2}' | tr -d " ")
    echo "${_CORES:-1}"
}

# owner resource user
owner() {
    _PATH=$1
    _OWNER=$2
    if [ ! -f "$_PATH" ] && [ ! -d "$_PATH" ]
    then
        mkdir -p "$_PATH"
    fi

    _CURRENT_OWNER=$(stat -c %U "$_PATH" 2> /dev/null)
    if [ "$_CURRENT_OWNER" != "$_OWNER" ]
    then
        chown -R "$_OWNER:$_OWNER" "$_PATH"
    fi
}

get_settings() {
    send_message "reading settings"
    if ! [ -f "$_SETTINGS" ]
    then
        cp /default_settings.py "$_SETTINGS"
    fi
    _HOST=$(get_migasfree_setting "DATABASES['default']['HOST']")
    _PORT=$(get_migasfree_setting "DATABASES['default']['PORT']")
    _USER=$(get_migasfree_setting "DATABASES['default']['USER']")
    _NAME=$(get_migasfree_setting "DATABASES['default']['NAME']")
    _PASSWORD=$(get_migasfree_setting "DATABASES['default']['PASSWORD']")
}

set_permissions() {
    send_message "setting permissions"
    _TARGET_USER=www-data

    # owner for repositories
    _PUBLIC_PATH=$(get_migasfree_setting MIGASFREE_PUBLIC_DIR)
    owner "$_PUBLIC_PATH" "$_TARGET_USER"

    # owner for keys
    _KEYS_PATH=$(get_migasfree_setting MIGASFREE_KEYS_DIR)
    owner "$_KEYS_PATH" "$_TARGET_USER"
    chmod 700 "$_KEYS_PATH"
}

run_as_www_data() {
    su www-data -s /bin/sh -c "$1"
}

is_db_empty() {
    send_message "checking database is empty"
    _RET=$(PGPASSWORD="$_PASSWORD" psql -h "$_HOST" -p "$_PORT" -U "$_USER" "$_NAME" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_type='BASE TABLE' and table_schema='public';")
    [ "${_RET:-1}" -eq 0 ]
}

is_db_exists() {
    send_message "checking is exists database"
    PGPASSWORD="$(get_secret_pass)" psql -h "$_HOST" -p "$_PORT" -U "$POSTGRES_USER" -tAc "SELECT 1 from pg_database WHERE datname='$_NAME'" 2> /dev/null | grep -q 1
}

is_user_exists() {
    send_message "checking user exists in database"
    PGPASSWORD="$(get_secret_pass)" psql -h "$_HOST" -p "$_PORT" -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$_USER';" | grep -q 1
}

create_db_user() {
    send_message "creating user in database"
    PGPASSWORD="$(get_secret_pass)" psql -h "$_HOST" -p "$_PORT" -U "$POSTGRES_USER" -tAc "CREATE USER \"$_USER\" WITH CREATEDB ENCRYPTED PASSWORD '$_PASSWORD';"
}

create_database() {
    send_message "creating database"
    PGPASSWORD="$(get_secret_pass)" psql -h "$_HOST" -p "$_PORT" -U "$POSTGRES_USER" -tAc "CREATE DATABASE \"$_NAME\" WITH OWNER = \"$_USER\" ENCODING='UTF8';"
}

migrate() {
    send_message "running database migrations"
    su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin migrate auth" www-data
    if [ "$1" = "fake-initial" ]
    then
        su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin migrate --fake-initial" www-data
    else
        su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin migrate" www-data
    fi
}

apply_fixtures() {
    send_message "applying fixtures to database"
    su -c "DJANGO_SETTINGS_MODULE=migasfree.settings.production django-admin initialize_db --skip-fixtures --force" www-data
    su -c "python3 -" www-data <<EOF
import django
from django.core.management import call_command
from io import StringIO
from django.db import connection
import os

django.setup()

from migasfree.fixtures import create_initial_data

create_initial_data()

# Custom sequence reset to avoid 'su postgres' error
commands = StringIO()
os.environ['DJANGO_COLORS'] = 'nocolor'
label_apps = ['core', 'client', 'device', 'hardware', 'stats', 'app_catalog']
for label in label_apps:
    call_command('sqlsequencereset', label, stdout=commands)

sql = commands.getvalue()
if sql:
    with connection.cursor() as cursor:
        cursor.execute(sql)
EOF
}

create_superuser() {
    _USERNAME=$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_name")
    _PASSWD=$(cat "${MIGASFREE_SECRET_DIR}/${STACK}_superadmin_pass")
    _EMAIL=""
    _PY_COMMAND="
import os
import django
from migasfree.core.models.user_profile import UserProfile
django.setup()
def create_superuser(username,  password, email):
    if not UserProfile.objects.filter(username=username).exists():
        UserProfile.objects.create_superuser(username=username, password=password, email=email)
        print('Superuser created successfully')
create_superuser('${_USERNAME}', '${_PASSWD}', '${_EMAIL}' )
"
    run_as_www_data "django-admin shell --settings=migasfree.settings.production -c \"${_PY_COMMAND}\"" >/dev/null
}


migasfree_init() {
    set_permissions

    is_db_exists || create_database
    is_user_exists || create_db_user

    if is_db_empty
    then
        send_message "empty database, running migrations and fixtures"
        echo yes | migrate "fake-initial"
        apply_fixtures
    else
        send_message "checking for pending migrations"
        if su -c "django-admin showmigrations | grep '\[ \]' " www-data > /dev/null
        then
            migrate ""
            apply_fixtures
        fi
    fi

    create_superuser
}


# START
# =====

export MIGASFREE_CONF_DIR=/var/lib/migasfree-backend/conf
mkdir -p "$(dirname "${MIGASFREE_CONF_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/conf" "${MIGASFREE_CONF_DIR}"

export MIGASFREE_PUBLIC_DIR=/var/lib/migasfree-backend/public
mkdir -p "$(dirname "${MIGASFREE_PUBLIC_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/public" "${MIGASFREE_PUBLIC_DIR}"

export MIGASFREE_KEYS_DIR=/var/lib/migasfree-backend/keys
mkdir -p "$(dirname "${MIGASFREE_KEYS_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/keys" "${MIGASFREE_KEYS_DIR}"

export MIGASFREE_TMP_DIR=/var/lib/migasfree-backend/tmp
mkdir -p "$(dirname "${MIGASFREE_TMP_DIR}")"
ln -snf "${DATASHARE_MOUNT_PATH}/tmp" "${MIGASFREE_TMP_DIR}"

# shellcheck source=/dev/null
. /venv/bin/activate

send_message "waiting datastore"
wait_for_service "$REDIS_HOST" "$REDIS_PORT"

send_message "waiting database"
wait_for_service "$POSTGRES_HOST" "$POSTGRES_PORT"

start_message
set_tz

if [ "$SERVICE" = "${STACK}_core" ]
then
    get_settings
    update_ca_certificates_action
    migasfree_init
    _PROCESS=$(pip freeze | grep daphne || :)
else
    _PROCESS=$(pip freeze | grep celery || :)
fi

show_banner "$_PROCESS"

send_message ""

if [ "$SERVICE" = "${STACK}_beat" ]
then
    # BEAT
    exec env DJANGO_SETTINGS_MODULE=migasfree.settings.production celery -A migasfree beat --uid=www-data --pidfile /var/tmp/celery.pid --schedule /var/tmp/celerybeat-schedule --loglevel INFO
elif [ "$SERVICE" = "${STACK}_worker" ]
then
    # WORKER
    /usr/bin/migrate_db &
    exec env DJANGO_SETTINGS_MODULE=migasfree.settings.production celery -A migasfree worker --queues="${QUEUES}" --uid 890 --without-gossip --loglevel INFO
else
    # CORE
    _WORKERS=$((2 * $(ncores) + 1))
    exec su -c "uvicorn migasfree.asgi:application --lifespan off --host 0.0.0.0 --port 8080 --workers $_WORKERS" www-data
fi

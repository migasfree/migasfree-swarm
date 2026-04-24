#!/bin/bash

# shellcheck source=/dev/null
. ../config/env/stack

# Helpers
function get_be_container {
    docker ps | grep "${STACK}_core" | awk '{print $1}' | head -n 1
}

function wait_for_be {
    echo "Waiting for core container to be ready..."
    _TIMEOUT=30
    _COUNT=0
    while [ -z "$(get_be_container)" ] && [ $_COUNT -lt $_TIMEOUT ]; do
        sleep 2
        _COUNT=$((_COUNT + 2))
    done
    if [ $_COUNT -ge $_TIMEOUT ]; then
        echo "Error: Core container timed out."
        exit 1
    fi
    sleep 5 # Extra buffer for Gunicorn to start
}

OLD_HOST=$1
OLD_PORT=$2
OLD_DB=${3:-migasfree}
OLD_USER=${4:-migasfree}
OLD_PWD=${5:-migasfree}

if [ -z "$OLD_HOST" ] || [ -z "$OLD_PORT" ]; then
    echo "Syntax: migrate-db OLD_HOST OLD_PORT [OLD_DB] [OLD_USER] [OLD_PWD]"
    exit 1
fi

echo
echo "WARNING: This process will replace the current v5 database with data from v4."
read -r -p "Target: $OLD_HOST:$OLD_PORT. Are you sure [yes/N]? "
echo

if [[ $REPLY != "yes" ]]; then
    exit 0
fi

# 1. SCALE DOWN
echo "Scaling down services..."
_REPLICAS_BE=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' "${STACK}_core")
_REPLICAS_FE=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' "${STACK}_console")
docker service scale "${STACK}_core=0" "${STACK}_console=0"
echo "***** CORE & CONSOLE: DISABLED *****"

# 2. DATA MIGRATION
echo "Migrating relational data from v4..."
DB_V5=$(docker ps | grep "${STACK}_database" | awk '{print $1}')
/usr/bin/time -f "Time DATA MIGRATION: %E" docker exec "${DB_V5}" bash -c "echo yes | bash /usr/share/migration/migrate_from_v4 $OLD_HOST $OLD_PORT $OLD_DB $OLD_USER $OLD_PWD"

# 3. SCALE UP
echo "Scaling up services..."
docker service scale "${STACK}_core=$_REPLICAS_BE" "${STACK}_console=$_REPLICAS_FE"
wait_for_be
BE_V5=$(get_be_container)
echo "***** CORE & CONSOLE: ENABLED *****"

# 4. INITIALIZE V5 SYSTEM USERS
echo "Initializing v5 system users and permissions..."
docker exec "${BE_V5}" bash -c "rm -f /tmp/migasfree.log && export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin initialize_db"

# 5. GENERATE TEMPORARY MIGRATION TOKEN
echo "Generating migration token..."
# We use a shell command to find the first superuser and get/create a token
MIG_TOKEN=$(docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin shell -c \"from django.contrib.auth.models import User; from rest_framework.authtoken.models import Token; user=User.objects.filter(is_superuser=True).first(); token, _ = Token.objects.get_or_create(user=user); print(token.key)\" | tail -n 1")

# 6. POPULATE REDIS CACHE (2010 to Present)
echo "Populating Redis metrics..."
_YEAR=$(date +"%Y")
while [ "$_YEAR" -ge 2010 ]; do
    echo "Processing year ${_YEAR} ..."
    /usr/bin/time -f "Time ${_YEAR}: %E" docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin refresh_redis_syncs --since $_YEAR --until $_YEAR > /dev/null"
    _YEAR=$((_YEAR - 1))
done

# 7. PACKAGE MIGRATION
echo
read -r -p "Do you want to migrate packages and projects now? (Make sure the v4 'STORES' directory is copied/mounted into the new volume) [yes/N]? "
if [[ $REPLY = "yes" ]]; then
    echo "Migrating packages and normalizing projects..."
    # We use localhost:8080 to avoid proxy issues during migration
    /usr/bin/time -f "Time PACKAGE MIGRATION: %E" docker exec -e MIGASFREE_TOKEN="$MIG_TOKEN" -e MIGASFREE_FQDN="localhost:8080" "${BE_V5}" bash -c "migrate-packages"
fi

echo "Migration finished successfully."

#!/bin/bash

# Try to load stack config from common locations
_STACK_BACKUP=$STACK
if [ -f "../config/env/stack" ]; then
    . ../config/env/stack
elif [ -f "../../migasfree-stack/config/env/stack" ]; then
    . ../../migasfree-stack/config/env/stack
fi

# Restore STACK if it was provided via environment
export STACK=${_STACK_BACKUP:-${STACK:-devel}}

# Helpers
function get_be_container {
    docker ps | grep "${STACK}_core" | awk '{print $1}' | head -n 1
}

function wait_for_be {
    echo "Waiting for core container to be ready..."
    _TIMEOUT=60
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
echo "WARNING: This process will replace the current v5 database ($STACK) with data from v4."
read -r -p "Target: $OLD_HOST:$OLD_PORT. Are you sure [yes/N]? "
echo

if [[ $REPLY != "yes" ]]; then
    exit 0
fi

# 1. SCALE DOWN
echo "Scaling down services..."
_REPLICAS_BE=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' "${STACK}_core" 2>/dev/null || echo 1)
_REPLICAS_FE=$(docker service inspect --format='{{.Spec.Mode.Replicated.Replicas}}' "${STACK}_console" 2>/dev/null || echo 1)
docker service scale "${STACK}_core=0" "${STACK}_console=0"
echo "***** CORE & CONSOLE: DISABLED *****"

# 2. DATA MIGRATION
echo "Migrating relational data from v4..."
DB_V5=$(docker ps --format "{{.ID}} {{.Names}}" | grep "${STACK}_database" | grep -v "console" | awk '{print $1}' | head -n 1)
if [ -z "$DB_V5" ]; then
    echo "Error: Database container for stack $STACK not found."
    exit 1
fi
time docker exec "${DB_V5}" bash -c "echo yes | bash /usr/share/migration/migrate_from_v4 $OLD_HOST $OLD_PORT $OLD_DB $OLD_USER $OLD_PWD"

# 3. SCALE UP
echo "Scaling up services..."
docker service scale "${STACK}_core=$_REPLICAS_BE" "${STACK}_console=$_REPLICAS_FE"
wait_for_be
BE_V5=$(get_be_container)
echo "***** CORE & CONSOLE: ENABLED (Container: $BE_V5) *****"

# 3.1 NORMALIZE BASIC ATTRIBUTES (All Systems Case Sensitivity)
echo "Normalizing 'All Systems' attribute (v4 ALL SYSTEMS -> v5 All Systems)..."
docker exec "${DB_V5}" psql -U migasfree -d migasfree -c "UPDATE core_attribute SET value = 'All Systems' WHERE id = 1 AND value = 'ALL SYSTEMS';"

# 4. INITIALIZE V5 SYSTEM USERS & PERMISSIONS
echo "Initializing v5 system users and permissions..."
docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin initialize_db && django-admin shell -c 'from django.contrib.auth.models import Group; [g.save() for g in Group.objects.all()]; print(\"Permissions regenerated for all groups.\")'"

# 4.0 ENSURE BASIC DATA INTEGRITY (All Systems, etc.)
echo "Ensuring basic data integrity (All Systems, etc.)..."
docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin loaddata core.property core.attribute"

# 4.1 FUSE LEGACY GROUPS
echo "Fusing legacy v4 groups into v5 standard groups..."
docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin shell -c \"
from django.contrib.auth.models import Group
MAPPING = {
    'Read': 'Reader',
    'Computers': 'Reader',
    'Query': 'Reader',
    'device add': 'Device installer',
    'device management': 'Device installer',
    'Devices': 'Device installer',
    'Check': 'Computer Checker',
    'Change Software Configuration': 'Liberator',
    'System': 'Domain Admin',
    'Conjuntos Change': 'Configurator',
}
for old_name, new_name in MAPPING.items():
    try:
        old_group = Group.objects.get(name=old_name)
        if old_name == new_name:
            continue
        new_group, _ = Group.objects.get_or_create(name=new_name)
        users = list(old_group.user_set.all())
        if users:
            new_group.user_set.add(*users)
        old_group.delete()
        print(f'Fused group \\'{old_name}\\' into \\'{new_name}\\'')
    except Group.DoesNotExist:
        pass
\""

# 5. GENERATE TEMPORARY MIGRATION TOKEN
echo "Generating migration token..."
MIG_TOKEN=$(docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin shell -c \"from django.contrib.auth.models import User; from rest_framework.authtoken.models import Token; user=User.objects.filter(is_superuser=True).first(); token, _ = Token.objects.get_or_create(user=user); print(token.key)\" | tail -n 1")

if [ -z "$MIG_TOKEN" ]; then
    echo "Error: Could not generate migration token."
else
    echo "Token generated: ${MIG_TOKEN:0:5}..."
fi

# 6. POPULATE REDIS CACHE (2010 to Present - Parallelized)
echo "Populating Redis metrics (Parallel Mode)..."
_YEAR=$(date +"%Y")
_MAX_PARALLEL=$(nproc)
if [ "$_MAX_PARALLEL" -lt 1 ]; then _MAX_PARALLEL=1; fi
_CURRENT_JOBS=0

while [ "$_YEAR" -ge 2010 ]; do
    echo "Processing year ${_YEAR} in background..."
    docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin refresh_redis_syncs --since $_YEAR --until $_YEAR > /dev/null" &
    
    _CURRENT_JOBS=$((_CURRENT_JOBS + 1))
    _YEAR=$((_YEAR - 1))

    if [ $_CURRENT_JOBS -ge $_MAX_PARALLEL ]; then
        wait
        _CURRENT_JOBS=0
        echo "Batch finished. Next batch..."
    fi
done
wait
echo "Populating Redis deployment stats..."
docker exec "${BE_V5}" bash -c "export DJANGO_SETTINGS_MODULE=migasfree.settings.production && . /venv/bin/activate && django-admin refresh_redis_deployments > /dev/null"
echo "Redis population finished."

# 7. PACKAGE MIGRATION
echo
read -r -p "Do you want to migrate packages and projects now? [yes/N]? "
if [[ $REPLY = "yes" ]]; then
    echo "Migrating packages and normalizing projects..."
    time docker exec -e MIGASFREE_TOKEN="$MIG_TOKEN" -e MIGASFREE_FQDN="localhost:8080" "${BE_V5}" bash -c "migrate-packages"
fi

echo "Migration finished successfully."

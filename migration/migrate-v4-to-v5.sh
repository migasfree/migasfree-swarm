#!/bin/bash

# Migasfree v4 to v5 Deterministic Migration Script
set -e

export STACK=${STACK:-devel}
MIGRATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/migration_v5_$(date +%Y%m%d_%H%M%S).log"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

function log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

function error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

function get_core_container() {
    docker ps | grep "${STACK}_core" | awk '{print $1}' | head -n 1
}

function fix_log_perms() {
    _CONT=$1
    _USER=$2
    docker exec "$_CONT" bash -c "touch /tmp/migasfree.log && chown $_USER:$_USER /tmp/migasfree.log && chmod 666 /tmp/migasfree.log"
}

# Arguments
OLD_HOST=$1; OLD_PORT=$2; OLD_DB=${3:-migasfree}; OLD_USER=${4:-migasfree}; OLD_PWD=${5:-migasfree}; DUMP_FILE=$6

if [ -z "$OLD_HOST" ] || [ -z "$OLD_PORT" ]; then
    echo "Usage: $0 OLD_HOST OLD_PORT [OLD_DB] [OLD_USER] [OLD_PWD] [DUMP_FILE_PATH]"
    exit 1
fi

START_TOTAL=$(date +%s)

# 1. Restore dump
if [ -n "$DUMP_FILE" ]; then
    log "Restoring dump in temporary container..."
    CONTAINER_V4="db-migration-v4-$(date +%s)"
    docker run -d --name "$CONTAINER_V4" -e POSTGRES_DB="$OLD_DB" -e POSTGRES_USER="$OLD_USER" -e POSTGRES_PASSWORD="$OLD_PWD" -p "$OLD_PORT:5432" postgres:13 > /dev/null
    sleep 10
    cat "$DUMP_FILE" | docker exec -i "$CONTAINER_V4" psql -U "$OLD_USER" "$OLD_DB" > /dev/null 2>&1 || true
    OLD_HOST=$(hostname -I | awk '{print $1}')
fi

# 2. Schema Initialization
log "Initializing v5 schema..."
CORE_CONTAINER=$(get_core_container)
fix_log_perms "$CORE_CONTAINER" "root"
docker exec "$CORE_CONTAINER" bash -c ". /venv/bin/activate && export DJANGO_SETTINGS_MODULE=migasfree.settings.production && django-admin initialize_db" >> "$LOG_FILE" 2>&1
fix_log_perms "$CORE_CONTAINER" "www-data"

# 3. Relational Migration
log "Starting Relational Database Migration..."
START_REL=$(date +%s)
printf "yes\nno\n" | bash "$MIGRATION_DIR/migrate-db.sh" "$OLD_HOST" "$OLD_PORT" "$OLD_DB" "$OLD_USER" "$OLD_PWD" >> "$LOG_FILE" 2>&1
END_REL=$(date +%s)
DIFF_REL=$((END_REL - START_REL))

# 4. Redis Population
log "Populating Redis metrics..."
CORE_CONTAINER=$(get_core_container)
fix_log_perms "$CORE_CONTAINER" "root"
START_REDIS=$(date +%s)
docker exec "$CORE_CONTAINER" bash -c ". /venv/bin/activate && export DJANGO_SETTINGS_MODULE=migasfree.settings.production && django-admin refresh_redis_syncs" >> "$LOG_FILE" 2>&1
END_REDIS=$(date +%s)
DIFF_REDIS=$((END_REDIS - START_REDIS))
fix_log_perms "$CORE_CONTAINER" "www-data"

# 5. Package Migration
log "Migrating packages..."
START_PKG=$(date +%s)
fix_log_perms "$CORE_CONTAINER" "root"
MIG_TOKEN=$(docker exec "$CORE_CONTAINER" bash -c ". /venv/bin/activate && export DJANGO_SETTINGS_MODULE=migasfree.settings.production && echo \"from django.contrib.auth.models import User; from rest_framework.authtoken.models import Token; user=User.objects.filter(is_superuser=True).first(); token, _ = Token.objects.get_or_create(user=user); print(token.key)\" | django-admin shell" | tail -n 1)

if [ -n "$MIG_TOKEN" ]; then
    docker exec -e MIGASFREE_TOKEN="$MIG_TOKEN" -e MIGASFREE_FQDN="localhost:8080" "$CORE_CONTAINER" bash -c "migrate-packages" >> "$LOG_FILE" 2>&1 || true
fi
fix_log_perms "$CORE_CONTAINER" "www-data"
END_PKG=$(date +%s)
DIFF_PKG=$((END_PKG - START_PKG))

# 6. Cleanup
[ -n "$CONTAINER_V4" ] && docker rm -f "$CONTAINER_V4" > /dev/null || true

# 7. Final Report
END_TOTAL=$(date +%s)
DIFF_TOTAL=$((END_TOTAL - START_TOTAL))
log "================================================="
log "MIGRATION COMPLETED"
log "Total time: $DIFF_TOTAL s"
log "- Relational DB: $DIFF_REL s"
log "- Redis Stats:   $DIFF_REDIS s"
log "- Packages/Meta: $DIFF_PKG s"
log "================================================="

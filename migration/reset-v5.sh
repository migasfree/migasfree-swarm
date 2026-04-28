#!/bin/bash

# Reset Migasfree v5 Environment (DB and Redis)

set -e

export STACK=${STACK:-devel}

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Resetting Migasfree v5 environment (Stack: $STACK)...${NC}"

# 1. Reset Database
echo "Resetting PostgreSQL database..."
DB_CONTAINER=$(docker ps | grep "${STACK}_database" | grep -v "console" | awk '{print $1}' | head -n 1)
if [ -z "$DB_CONTAINER" ]; then
    echo "Error: Database container not found."
    exit 1
fi

docker exec "$DB_CONTAINER" psql -U migasfree -d template1 -c "DROP DATABASE IF EXISTS migasfree;"
docker exec "$DB_CONTAINER" psql -U migasfree -d template1 -c "CREATE DATABASE migasfree OWNER migasfree;"
echo "Database 'migasfree' recreated."

# 2. Reset Redis
echo "Resetting Redis (Datastore)..."
DATASTORE_CONTAINER=$(docker ps | grep "${STACK}_datastore" | grep -v "console" | awk '{print $1}' | head -n 1)
if [ -z "$DATASTORE_CONTAINER" ]; then
    echo "Error: Datastore container not found."
    exit 1
fi

REDIS_PASS=$(docker exec "$DATASTORE_CONTAINER" cat "/run/secrets/${STACK}_superadmin_pass")
docker exec "$DATASTORE_CONTAINER" redis-cli -a "$REDIS_PASS" flushall
echo "Redis cache flushed."

# 3. Cleanup Logs
echo "Cleaning up logs..."
CORE_CONTAINER=$(docker ps | grep "${STACK}_core" | awk '{print $1}' | head -n 1)
if [ -n "$CORE_CONTAINER" ]; then
    docker exec "$CORE_CONTAINER" rm -f /tmp/migasfree.log
    echo "Log file /tmp/migasfree.log removed."
fi

echo -e "${GREEN}Reset complete.${NC}"

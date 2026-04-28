#!/bin/bash

# Reset Migasfree v5 Environment (DB and Redis)

set -e

if [ -z "$STACK" ]; then
    # Auto-discover stack name from core service
    STACK=$(docker service ls --format '{{.Name}}' | grep '_core$' | sed 's/_core$//' | head -n 1)
fi
export STACK=${STACK:-devel}

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Resetting Migasfree v5 environment (Stack: $STACK)...${NC}"

# 0. Scale down services to close connections
echo "Scaling down services..."
docker service scale ${STACK}_core=0 ${STACK}_console=0 ${STACK}_manager=0 ${STACK}_public=0 ${STACK}_worker=0 ${STACK}_beat=0 ${STACK}_mcp-server=0 ${STACK}_tunnel=0

# 1. Reset Database
echo "Resetting PostgreSQL database..."
DB_CONTAINER=$(docker ps | grep "${STACK}_database" | grep -v "console" | awk '{print $1}' | head -n 1)
if [ -z "$DB_CONTAINER" ]; then
    echo "Error: Database container not found."
    exit 1
fi

docker exec "$DB_CONTAINER" psql -U migasfree -d template1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'migasfree' AND pid <> pg_backend_pid();"
docker exec "$DB_CONTAINER" psql -U migasfree -d template1 -c "DROP DATABASE IF EXISTS migasfree;"
docker exec "$DB_CONTAINER" psql -U migasfree -d template1 -c "CREATE DATABASE migasfree OWNER migasfree;"
echo "Database 'migasfree' recreated."

# 2. Reset Redis
echo "Resetting Redis cache..."
DATASTORE_CONTAINER=$(docker ps --filter "name=${STACK}_datastore\." --format '{{.ID}}' | head -n 1)
if [ -z "$DATASTORE_CONTAINER" ]; then
    echo "Error: Datastore container not found."
    exit 1
fi

REDIS_PASS=$(docker exec "$DATASTORE_CONTAINER" cat "/run/secrets/${STACK}_superadmin_pass")
docker exec "$DATASTORE_CONTAINER" redis-cli -a "$REDIS_PASS" flushall
echo "Redis cache flushed."

# 3. Scale up services
echo "Scaling up services..."
docker service scale ${STACK}_core=1 ${STACK}_console=1 ${STACK}_manager=1 ${STACK}_public=1 ${STACK}_worker=1 ${STACK}_beat=1 ${STACK}_mcp-server=1 ${STACK}_tunnel=1

echo -e "${GREEN}Reset complete.${NC}"

#!/bin/bash

# Load password from secret if available
if [ -f "$POSTGRES_PASSWORD_FILE" ]; then
    DB_PASSWORD=$(cat "$POSTGRES_PASSWORD_FILE")
    export DB_PASSWORD
fi

PCP_PORT="${PCP_PORT:-9898}"
PCP_USER="${POSTGRES_USER:-postgres}"

# 1. Check if pgpool process is running
if ! pgrep pgpool > /dev/null; then
    echo "Pgpool process not found"
    exit 1
fi

# 2. Check if pcp_node_count works (verifies PCP authentication and socket accessibility)
if ! pcp_node_count -h localhost -p "$PCP_PORT" -U "$PCP_USER" -w > /dev/null 2>&1; then
    echo "PCP interface not responding"
    exit 1
fi

# 3. Check if at least one backend node is 'up' (status 1 or 2)
# Status codes: 0: Init, 1: Standby 'up', 2: Master 'up', 3: Down
status_output=$(pcp_node_info -h localhost -p "$PCP_PORT" -U "$PCP_USER" -w)
if ! echo "$status_output" | awk '{print $3}' | grep -E "1|2" > /dev/null; then
    echo "No backend nodes available"
    exit 1
fi

exit 0

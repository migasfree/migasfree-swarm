#!/bin/bash
set -e

# Load password from secret if available
if [ -f "$POSTGRES_PASSWORD_FILE" ]; then
    export DB_PASSWORD=$(cat "$POSTGRES_PASSWORD_FILE")
fi

# ==========================================
# Constants
# ==========================================

PGPOOL_PIDFILE="/var/run/pgpool/pgpool_main.pid"
BACKENDS_STATE="/var/run/pgpool/backends.state"
RESTART_FLAG="/var/run/pgpool/restart_requested"
PCP_PORT=9898
PCP_USER="$POSTGRES_USER"
PCP_PASSWORD="$DB_PASSWORD"

# Port Configuration
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
PORT_DATABASE="${PORT_DATABASE:-5432}"

# ==========================================
# Functions
# ==========================================

# Build pgpool backend config block for a given node_id, ip, role
backend_config_block() {
    local node_id="$1"
    local ip="$2"
    local role="$3"

    local flag
    local weight
    if [ "$role" = "PRIMARY" ]; then
        flag="ALWAYS_PRIMARY|ALLOW_TO_FAILOVER"
        weight=0  # Primary handles only writes and transactional queries
    else
        flag="ALLOW_TO_FAILOVER"
        weight=1  # Replicas handle all non-transactional reads
    fi

    cat <<BLOCK
# Backend $node_id: $role
backend_hostname${node_id} = '$ip'
backend_port${node_id} = $PORT_DATABASE
backend_weight${node_id} = $weight
backend_flag${node_id} = '$flag'
BLOCK
}

# Build backends config from static IPs
generate_backends_from_static() {
    local backend_id=0
    local backends=""
    local state=""

    echo "    $PRIMARY_IP → PRIMARY (backend_$backend_id)"
    backends="${backends}
$(backend_config_block $backend_id "$PRIMARY_IP" "PRIMARY")
"
    state="${state}${backend_id}:${PRIMARY_IP}:PRIMARY
"
    backend_id=$((backend_id + 1))

    # Process Comma-separated or Space-separated REPLICAS_IP list
    if [ -n "$REPLICAS_IP" ]; then
        local replica_list
        replica_list=$(echo "$REPLICAS_IP" | tr ',' ' ')
        for IP in $replica_list; do
            echo "    $IP → REPLICA (backend_$backend_id)"
            backends="${backends}
$(backend_config_block $backend_id "$IP" "REPLICA")
"
            state="${state}${backend_id}:${IP}:REPLICA
"
            backend_id=$((backend_id + 1))
        done
    fi

    PGPOOL_BACKENDS="$backends"
    BACKEND_COUNT=$backend_id
    
    mkdir -p /var/run/pgpool
    echo "$state" > "$BACKENDS_STATE"
    return 0
}

generate_pgpool_conf() {
    cat <<EOF > /etc/pgpool/pgpool.conf
listen_addresses = '*'
port = $POSTGRES_PORT
pcp_port = $PCP_PORT
socket_dir = '/var/run/pgpool'
pcp_socket_dir = '/var/run/pgpool'

$PGPOOL_BACKENDS

# Streaming Replication mode
master_slave_mode = on
master_slave_sub_mode = 'stream'
replication_mode = off
load_balance_mode = on

# Health Check (direct to each backend)
health_check_period = 3
health_check_timeout = 2
health_check_user = '$POSTGRES_USER'
health_check_password = '$DB_PASSWORD'
health_check_database = 'postgres'
health_check_max_retries = 2
health_check_retry_delay = 1

# Failover behavior
failover_on_backend_error = off
failover_on_backend_shutdown = off
search_primary_node_timeout = 10

# Auto failback: re-attach recovered standbys automatically
auto_failback = on
auto_failback_interval = 5

# Detach false primaries (safety net for split-brain)
detach_false_primary = on

# Streaming Replication Check
sr_check_period = 5
sr_check_user = '$POSTGRES_USER'
sr_check_password = '$DB_PASSWORD'
sr_check_database = 'postgres'

# Connection Pool
connection_cache = on
max_pool = 4
num_init_children = 32

# Authentication
enable_pool_hba = on
pool_passwd = '/etc/pgpool/pool_passwd'

# Logging
log_statement = on
log_per_node_statement = on
EOF
}

setup_pcp() {
    # Generate md5 hash for PCP authentication
    local pcp_md5
    pcp_md5=$(pg_md5 "$PCP_PASSWORD")
    echo "${PCP_USER}:${pcp_md5}" > /etc/pgpool/pcp.conf

    # Create .pcppass for passwordless PCP commands
    echo "localhost:${PCP_PORT}:${PCP_USER}:${PCP_PASSWORD}" > ~/.pcppass
    chmod 600 ~/.pcppass
}

# ==========================================
# Pgpool process management
# ==========================================

start_pgpool() {
    echo "Starting Pgpool-II..."
    pgpool -n -f /etc/pgpool/pgpool.conf &
    echo $! > "$PGPOOL_PIDFILE"
    echo "Pgpool-II started (PID $(cat $PGPOOL_PIDFILE))"
}

stop_pgpool() {
    local pid
    pid=$(cat "$PGPOOL_PIDFILE" 2>/dev/null)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "Stopping Pgpool-II (PID $pid)..."
        pgpool -m fast -f /etc/pgpool/pgpool.conf stop 2>/dev/null || kill -TERM "$pid" 2>/dev/null
        wait "$pid" 2>/dev/null || true
        echo "Pgpool-II stopped."
    fi
}

# ==========================================
# Dynamic Discovery
# ==========================================

# Discover PostgreSQL backends from Manager API (Node IPs)
discover_backends() {
    echo "Discovering PostgreSQL backends from Manager API..."
    
    # Query Manager API for backends
    local response
    response=$(curl -s "http://manager:8080/v1/internal/backends")
    
    if [ -z "$response" ] || [ "$response" = "[]" ]; then
        echo "  [discovery] No backends found from Manager yet."
        return 1
    fi
    
    local PRIMARY=""
    local REPLICAS=""
    
    # Parse JSON using jq
    PRIMARY=$(echo "$response" | jq -r '.[] | select(.role == "PRIMARY") | .ip' | head -n 1)
    REPLICAS=$(echo "$response" | jq -r '.[] | select(.role == "REPLICA") | .ip' | tr '\n' ',' | sed 's/,$//')

    if [ -z "$PRIMARY" ]; then
        echo "  [discovery] No primary database found in Manager response."
        return 1
    fi
    
    export PRIMARY_IP="$PRIMARY"
    export REPLICAS_IP="$REPLICAS"
    return 0
}

# ==========================================
# Initial configuration
# ==========================================

echo "Waiting for services to stabilize before discovery..."
sleep 10

echo "Starting dynamic backend discovery..."
until discover_backends; do
    echo "Retrying discovery in 5 seconds..."
    sleep 5
done

echo "Discovery complete:"
echo "  Primary: $PRIMARY_IP"
echo "  Replicas: $REPLICAS_IP"

echo "Generating PostgreSQL backends configuration..."
generate_backends_from_static

echo "Found $BACKEND_COUNT active backend(s)."

# ==========================================
# Generate config files
# ==========================================

echo "Generating pgpool.conf..."
generate_pgpool_conf

if [ -n "$POSTGRES_USER" ] && [ -n "$DB_PASSWORD" ]; then
    echo "Generating pool_passwd..."
    echo "${POSTGRES_USER}:${DB_PASSWORD}" > /etc/pgpool/pool_passwd
fi

cat <<EOF > /etc/pgpool/pool_hba.conf
# TYPE  DATABASE    USER        ADDRESS          METHOD
local   all         all                          trust
host    all         all         0.0.0.0/0        scram-sha-256
host    all         all         ::/0             scram-sha-256
EOF

mkdir -p /var/run/pgpool
chown -R postgres:postgres /var/run/pgpool /etc/pgpool

echo "Setting up PCP authentication..."
setup_pcp

# Forward signals to pgpool for clean container shutdown
cleanup() {
    echo "Received shutdown signal. Stopping all processes..."
    stop_pgpool
    exit 0
}
trap cleanup SIGTERM SIGINT

# ==========================================
# Auto-attach recovered nodes (Lightweight)
# ==========================================
(
    sleep 30  # wait for pgpool to stabilize
    echo "[auto-attach] Service started. Monitoring for recovered nodes..."
    while true; do
        sleep 15
        
        # We read all nodes and iterate with an index
        index=0
        while read -r line; do
            if [ -z "$line" ]; then continue; fi
            
            # Status code is the 3rd column
            status=$(echo "$line" | awk '{print $3}')
            ip=$(echo "$line" | awk '{print $1}')
            
            if [ "$status" = "3" ]; then
                # Node is DOWN. Check if it's reachable now.
                if nc -zv "$ip" "$PORT_DATABASE" >/dev/null 2>&1; then
                    echo "[auto-attach] Node $index ($ip) is reachable. Attempting to attach..."
                    pcp_attach_node -h localhost -p $PCP_PORT -U "$PCP_USER" -w "$index" || true
                fi
            fi
            index=$((index + 1))
        done < <(pcp_node_info -h localhost -p $PCP_PORT -U "$PCP_USER" -w)
    done
) &

# ==========================================
# Start Pgpool and keep container alive
# ==========================================

start_pgpool

# Supervision loop
while true; do
    CURRENT_PID=$(cat "$PGPOOL_PIDFILE" 2>/dev/null)
    if [ -n "$CURRENT_PID" ]; then
        wait "$CURRENT_PID" 2>/dev/null
        EXIT_CODE=$?
    fi

    # Pgpool exited unexpectedly — exit the container
    echo "Pgpool-II exited unexpectedly (code ${EXIT_CODE:-unknown}). Container will restart."
    exit ${EXIT_CODE:-1}
done

#!/bin/bash
set -e

. /usr/bin/common.sh
set_tz

load_secret "$(basename "$POSTGRES_PASSWORD_FILE")" "DB_PASSWORD"

# ==========================================
# Constants
# ==========================================

PGPOOL_PIDFILE="/var/run/pgpool/pgpool_main.pid"
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
    if [ "$role" = "PRIMARY" ]
    then
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
# Dynamic Discovery & Watchdog
# ==========================================

# Discover all Swarm Nodes
discover_topology() {
    local response
    response=$(curl -s "http://manager:8080/v1/internal/topology")
    if [ -z "$response" ] || [ "$response" = "{}" ]; then
        return 1
    fi
    mkdir -p /var/run/pgpool
    echo "$response" > /var/run/pgpool/topology.json
    return 0
}


# Generate pgpool.conf with fixed slots for each Swarm Node IP
generate_dynamic_config() {
    local backends=""
    local index=0
    
    local nodes_ips
    nodes_ips=$(jq -r '.nodes[].node_ip' /var/run/pgpool/topology.json)
    local primary_ip
    primary_ip=$(curl -s "http://manager:8080/v1/internal/backends" | jq -r '.[] | select(.role == "PRIMARY") | .ip')
    
    for node_ip in $nodes_ips
    do
        # Primary gets weight 0 (only writes). Replicas get weight 1 (reads).
        local weight=1
        if [ "$node_ip" = "$primary_ip" ]
        then
            weight=0
        fi
        
        backends="${backends}
# Backend $index -> Swarm Node: $node_ip
backend_hostname${index} = '${node_ip}'
backend_port${index} = ${PORT_DATABASE}
backend_weight${index} = ${weight}
backend_flag${index} = 'ALLOW_TO_FAILOVER'
"
        index=$((index + 1))
    done
    
    PGPOOL_BACKENDS="$backends"
    generate_pgpool_conf
}

# The Watchdog: Monitors and automatically attaches recovered DB nodes
start_topology_watchdog() {
    (
        echo "[watchdog] Starting Topology Watchdog..."
        sleep 30  # Wait for pgpool to stabilize 
        
        while true
        do
            if [ -f "$PGPOOL_PIDFILE" ]
            then
                local index=0
                local nodes_ips
                nodes_ips=$(jq -r '.nodes[].node_ip' /var/run/pgpool/topology.json)
                
                for node_ip in $nodes_ips
                do
                    local current_status
                    current_status=$(pcp_node_info -h localhost -p "$PCP_PORT" -U "$PCP_USER" -w "$index" | awk '{print $3}')
                    
                    if [ "$current_status" = "3" ]
                    then
                        # Node is marked down by pgpool. Check network availability
                        if nc -zv "$node_ip" "$PORT_DATABASE" >/dev/null 2>&1
                        then
                            echo "[watchdog] Node $index ($node_ip) is reachable again. Attempting to attach..."
                            pcp_attach_node -h localhost -p $PCP_PORT -U "$PCP_USER" -w $index || true
                        fi
                    fi
                    index=$((index + 1))
                done
            fi
            sleep 15
        done
    ) &
}

start_message
# Initial configuration

echo "Waiting for Manager topology API..."
until discover_topology
do
    echo "Retrying in 5 seconds..."
    sleep 5
done

echo "Topology discovered. Generating slots for $(jq '.nodes | length' /var/run/pgpool/topology.json) nodes."
generate_dynamic_config

start_topology_watchdog

# ==========================================
# Generate config files
# ==========================================

echo "Generating pgpool.conf..."
generate_pgpool_conf

if [ -n "$POSTGRES_USER" ] && [ -n "$DB_PASSWORD" ]
then
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
    while true
    do
        sleep 15
        
        # We read all nodes and iterate with an index
        index=0
        while read -r line
        do
            if [ -z "$line" ]; then continue; fi
            
            # Status code is the 3rd column
            status=$(echo "$line" | awk '{print $3}')
            ip=$(echo "$line" | awk '{print $1}')
            
            if [ "$status" = "3" ]
            then
                # Node is DOWN. Check if it's reachable now.
                if nc -zv "$ip" "$PORT_DATABASE" >/dev/null 2>&1
                then
                    echo "[auto-attach] Node $index ($ip) is reachable. Attempting to attach..."
                    pcp_attach_node -h localhost -p $PCP_PORT -U "$PCP_USER" -w "$index" || true
                fi
            fi
            index=$((index + 1))
        done < <(pcp_node_info -h localhost -p $PCP_PORT -U "$PCP_USER" -w)
    done
) &

show_banner "$(pgpool -v 2>&1)"

# ==========================================
# Start Pgpool and keep container alive
# ==========================================

start_pgpool

# Supervision loop
while true
do
    CURRENT_PID=$(cat "$PGPOOL_PIDFILE" 2>/dev/null)
    if [ -n "$CURRENT_PID" ]
    then
        wait "$CURRENT_PID" 2>/dev/null
        EXIT_CODE=$?
    fi

    # Pgpool exited unexpectedly — exit the container
    echo "Pgpool-II exited unexpectedly (code ${EXIT_CODE:-unknown}). Container will restart."
    exit "${EXIT_CODE:-1}"
done

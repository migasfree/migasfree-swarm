#!/bin/bash

# Set Timezone
if [ -n "$TZ" ] && [ -f "/usr/share/zoneinfo/$TZ" ]; then
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "$TZ" > /etc/timezone
    echo "Timezone set to: $TZ"
fi

set -e

function capture_message {
    local _LAST="database system is ready to accept connections"

    if [[ "$1" == *"$_LAST"* ]]
    then
        send_message "" &
    else
        send_message "$1" &
    fi
}


function cron_init
{
    if [ -z "$BACKUP_CRON" ]
    then
        BACKUP_CRON="0 0 * * *"
    fi
    CRON=$(echo "$BACKUP_CRON" | tr -d "'") # remove single quote
    echo "$CRON /usr/bin/backup" > /tmp/cron
    crontab /tmp/cron
    rm /tmp/cron

    crond -l 2 -f > /dev/stdout 2> /dev/stderr &
}


# Auto-detect Role
# We try various ways to get the current node hostname/id
CURRENT_NODE="${MY_NODE_HOSTNAME:-$NODE}"
# If still empty, try parsing from hostname (container ID) - last resort
if [ -z "$CURRENT_NODE" ]; then
    CURRENT_NODE=$(hostname)
fi

if [ -n "$POSTGRES_PRIMARY_NODE" ]; then
    if [ "$POSTGRES_PRIMARY_NODE" = "$CURRENT_NODE" ]; then
        echo "Node $CURRENT_NODE is the PRIMARY"
        export PG_ROLE="primary"
    else
        echo "Node $CURRENT_NODE is a REPLICA (Primary is $POSTGRES_PRIMARY_NODE)"
        export PG_ROLE="replica"
        # Connect directly to the primary database for replication,
        # bypassing proxy/pgpool which could route incorrectly
        export PG_PRIMARY_HOST="tasks.database"
    fi
fi

# Locate data directory accurately
if [ -z "$PGDATA" ]; then
    export PGDATA="/var/lib/postgresql/data"
    # Try to find existing data directory if any
    _FOUND_DATA=$(find /var/lib/postgresql -name postgresql.conf -exec dirname {} \; | head -n 1)
    if [ -n "$_FOUND_DATA" ]; then
        export PGDATA="$_FOUND_DATA"
    fi
fi

# Replication logic
if [ "$PG_ROLE" == "replica" ]
then
    # If the directory is not a valid postgres database (missing pg_control)
    if [ ! -f "$PGDATA/global/pg_control" ]
    then
        # PostgreSQL slot names must be lowercase and use underscores instead of hyphens
        SLOT_NAME=$(echo "slot_${CURRENT_NODE}" | tr '-' '_' | tr '[:upper:]' '[:lower:]')
        
        if [ -f "$REPLICATION_PASSWORD_FILE" ]; then
            export PGPASSWORD=$(cat "$REPLICATION_PASSWORD_FILE")
        fi

        # Discover the real primary IP from tasks.database
        echo "Discovering primary database IP..."
        PRIMARY_IP=""
        for IP in $(nslookup tasks.database 2>/dev/null | grep -A999 "Non-authoritative" | grep "Address:" | awk '{print $2}'); do
            IS_PRIMARY=$(PGPASSWORD="$PGPASSWORD" psql -h "$IP" -p 5432 -U "$REPLICATION_USER" -d postgres -tAc "SELECT NOT pg_is_in_recovery();" 2>/dev/null || echo "f")
            if [ "$IS_PRIMARY" = "t" ]; then
                PRIMARY_IP="$IP"
                echo "  Found primary at $IP"
                break
            fi
        done

        if [ -z "$PRIMARY_IP" ]; then
            echo "WARNING: Could not discover primary IP. Falling back to tasks.database"
            PRIMARY_IP="$PG_PRIMARY_HOST"
        fi

        echo "Valid database system not found in $PGDATA (pg_control missing)."
        echo "Wiping 'dirty' directory and starting fresh synchronization from $PRIMARY_IP using slot $SLOT_NAME..."
        
        rm -rf "$PGDATA"/*
        mkdir -p "$PGDATA"
        chown postgres:postgres "$PGDATA"

        # Ensure replication slot exists on primary
        echo "Ensuring replication slot '$SLOT_NAME' exists on primary..."
        psql -h "$PRIMARY_IP" -U "$REPLICATION_USER" -d postgres -c "
            DO \$\$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = '$SLOT_NAME') THEN
                    PERFORM pg_create_physical_replication_slot('$SLOT_NAME');
                END IF;
            END
            \$\$;
        " || true

        pg_basebackup -h "$PRIMARY_IP" -D "$PGDATA" -U "$REPLICATION_USER" -vP -R --slot="$SLOT_NAME"

        # Patch primary_conninfo to use tasks.database instead of the hardcoded IP
        # This ensures replication survives primary container restarts (IP changes)
        if [ -f "$PGDATA/postgresql.auto.conf" ]; then
            sed -i "s|host=$PRIMARY_IP|host=tasks.database|g" "$PGDATA/postgresql.auto.conf"
            echo "Patched primary_conninfo to use tasks.database instead of $PRIMARY_IP"
            grep primary_conninfo "$PGDATA/postgresql.auto.conf"
        fi

        unset PGPASSWORD
    fi
fi

# Primary Standby Cleanup
if [ "$PG_ROLE" == "primary" ]; then
    if [ -f "$PGDATA/standby.signal" ]; then
        echo "Primary role detected but standby.signal found. Removing it to allow writes..."
        rm "$PGDATA/standby.signal"
    fi
    # Also clean up replication settings in postgresql.auto.conf if any
    if [ -f "$PGDATA/postgresql.auto.conf" ]; then
        sed -i "/primary_conninfo/d" "$PGDATA/postgresql.auto.conf"
        sed -i "/primary_slot_name/d" "$PGDATA/postgresql.auto.conf"
    fi
fi


# Changes UID and GID for backup and restore in datashare
OWNER_UID=890
OWNER_GID=890
sed -e "/^postgres/s=^postgres:x:[0-9]*:[0-9]*:=postgres:x:${OWNER_UID}:${OWNER_GID}:=" -i /etc/passwd
sed -e "/^postgres/s=^postgres:x:[0-9]*:=postgres:x:${OWNER_GID}:=" -i /etc/group

# Ensure postgres user owns the data directory
chown -R postgres:postgres /var/lib/postgresql


# Write parameters in postgresql.conf
echo "Parameterization"
echo "================"
echo "$POSTGRESQL_CONF"
echo
# Function to apply parameters to postgresql.conf
function apply_postgresql_params {
    local config_file=$1
    if [ -f "$config_file" ]; then
        echo "Applying parameters to $config_file"
        IFS='|' read -ra PARAMS <<< "$POSTGRESQL_CONF"
        for param_value in "${PARAMS[@]}"; do
            param=$(echo $param_value | cut -d= -f1)
            value=$(echo $param_value | cut -d= -f2)
            if grep -q "^#*\s*${param}\s*=" "$config_file"; then
                sed -i "s|^#*\s*${param}\s*=.*|${param} = ${value}|" "$config_file"
            else
                echo "${param} = ${value}" >> "$config_file"
            fi
        done
    fi
}

# Locate postgresql.conf
CONFIG_FILE=$(find /var/lib/postgresql -name postgresql.conf | head -n 1)
if [ -z "$CONFIG_FILE" ]; then
    CONFIG_FILE="${PGDATA:-/var/lib/postgresql/data}/postgresql.conf"
fi

if [ -f "$CONFIG_FILE" ]; then
    apply_postgresql_params "$CONFIG_FILE"
else
    echo "PostgreSQL configuration file $CONFIG_FILE not found."
    echo "Creating initialization hook in /docker-entrypoint-initdb.d/99-config-params.sh"
    mkdir -p /docker-entrypoint-initdb.d
    cat <<EOF > /docker-entrypoint-initdb.d/99-config-params.sh
#!/bin/bash
# Find the actual config file after initialization
REAL_CONFIG=\$(find /var/lib/postgresql -name postgresql.conf | head -n 1)
if [ -n "\$REAL_CONFIG" ]; then
    echo "Initialization hook: Applying parameters to \$REAL_CONFIG"
    IFS='|' read -ra PARAMS <<< "$POSTGRESQL_CONF"
    for param_value in "\${PARAMS[@]}"; do
        param=\$(echo \$param_value | cut -d= -f1)
        value=\$(echo \$param_value | cut -d= -f2)
        if grep -q "^#*\s*\${param}\s*=" "\$REAL_CONFIG"; then
            sed -i "s|^#*\s*\${param}\s*=.*|\${param} = \${value}|" "\$REAL_CONFIG"
        else
            echo "\${param} = \${value}" >> "\$REAL_CONFIG"
        fi
    done
fi
EOF
    chmod +x /docker-entrypoint-initdb.d/99-config-params.sh
fi

# Function to ensure replication user exists with correct password
function ensure_replication_user {
    # Wait for postgres to be ready
    until pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; do
        sleep 5
    done

    echo "Ensuring replication user '$REPLICATION_USER' exists using local trust..."
    
    # We don't use PGPASSWORD here because we have 'trust' rule in pg_hba.conf for local
    psql -U "$POSTGRES_USER" -d postgres -c "
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$REPLICATION_USER') THEN
                CREATE USER $REPLICATION_USER WITH REPLICATION ENCRYPTED PASSWORD '$REPLICATION_PASSWORD';
            ELSE
                ALTER USER $REPLICATION_USER WITH REPLICATION ENCRYPTED PASSWORD '$REPLICATION_PASSWORD';
            END IF;
        END
        \$\$;
    "
}

# Replication user and HBA configuration (Primary only)
if [ "$PG_ROLE" == "primary" ] || [ -z "$PG_ROLE" ]
then
    if [ -f "$REPLICATION_PASSWORD_FILE" ]; then
        REPLICATION_PASSWORD=$(cat "$REPLICATION_PASSWORD_FILE")
    fi
    
    # Launch background task to ensure user existence
    # We unset PGPASSWORD here to force psql to use the 'trust' rule via socket
    (ensure_replication_user) &
fi

# --- GLOBAL pg_hba.conf OVERWRITE ---
# We do this at the very end to ensure all files are caught
for hba in $(find /var/lib/postgresql -name pg_hba.conf); do
    echo "Force updating $hba with broad internal trust..."
    cat <<EOF > "$hba"
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust

# Swarm Internal Network (Allow replication and all)
host    replication     $REPLICATION_USER 10.0.0.0/8            trust
host    all             all             10.0.0.0/8              trust

# Fallback for other connections (SCRAM)
host    replication     $REPLICATION_USER 0.0.0.0/0           scram-sha-256
host    all             all             0.0.0.0/0               scram-sha-256
EOF
done


send_message "starting ${SERVICE:(${#STACK})+1}" &
if [ "$PG_ROLE" == "primary" ] || [ -z "$PG_ROLE" ]
then
    cron_init
fi

echo "


                   █                          ██
                                             █
         ███ ██    █    ██     ███     ███  ████  ███  ███    ███
        █   █  █   █   █  █       █   █      █   █    █   █  █   █
        █   █  █   █   █  █    ████    ██    █   █    ████   ████
        █   █  █   █   █  █   █   █      █   █   █    █      █
        █   █  █   █    ███    ███    ███    █   █     ███    ███
                          █
        we love change  ██


        $SERVICE ($TAG)
        $(postgres -V)
        Container: $HOSTNAME
        Time zone: $TZ $(date)
        Processes: $(nproc)

"

send_message "" &

# if no database dump exists, one will be created (Primary only)
if [ "$PG_ROLE" == "primary" ] || [ -z "$PG_ROLE" ]
then
    if ! [ -f "${DATASHARE_MOUNT_PATH}/dump/migasfree.sql" ]
    then
        sh -c "sleep 60;backup" &
    fi
fi




echo "Starting PostgreSQL..."
exec /usr/local/bin/docker-entrypoint.sh postgres
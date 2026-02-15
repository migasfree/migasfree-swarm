#!/bin/bash

set -e

function capture_message {
    local _LAST="database system is ready to accept connections"

    if [[ "$1" == *"$_LAST"* ]]
    then
        send_message ""
    else
        send_message "$1"
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


if nc -z database 5432 >/dev/null 2>&1
then
   echo "WARNING: Only one database replica is allowed."
   exit 1
fi

# Changes UID and GID for backup and restore in datashare
OWNER_UID=890
OWNER_GID=890
sed -e "/^postgres/s=^postgres:x:[0-9]*:[0-9]*:=postgres:x:${OWNER_UID}:${OWNER_GID}:=" -i /etc/passwd
sed -e "/^postgres/s=^postgres:x:[0-9]*:=postgres:x:${OWNER_GID}:=" -i /etc/group


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


send_message "starting ${SERVICE:(${#STACK})+1}"
cron_init

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
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

send_message ""

# if no database dump exists, one will be created
if ! [ -f "${DATASHARE_MOUNT_PATH}/dump/migasfree.sql" ]
then
    sh -c "sleep 60;backup" &
fi

# Run docker-entrypoint.sh (from postgres image)
/usr/local/bin/docker-entrypoint.sh postgres

# Capture stdout line by line
#stdbuf -oL bash /usr/local/bin/docker-entrypoint.sh postgres |
#    while IFS= read -r _LINE
#    do
#        capture_message "$_LINE"
#    done

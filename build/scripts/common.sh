#!/bin/sh
# Migasfree Swarm Common Shell Library
# Standardized functions for initialization, waiting, and diagnostic reporting.

start_message() {
    _SERVICE_NAME=${SERVICE#${STACK:?}_}
    send_message "starting $_SERVICE_NAME"
}

set_tz() {
    _TZ="${1:-$TZ}"
    _TZ="${_TZ:-Europe/Madrid}"
    if [ -f "/usr/share/zoneinfo/$_TZ" ]
    then
        ln -snf "/usr/share/zoneinfo/$_TZ" /etc/localtime
        echo "$_TZ" > /etc/timezone
    fi
}

wait_for_service() {
    _SERVER="$1"
    _PORT="$2"
    _COUNTER=0
    until [ "$_COUNTER" -gt 60 ]
    do
        if nc -z "$_SERVER" "$_PORT" 2> /dev/null
        then
            echo "$_SERVER:$_PORT is running."
            return 0
        else
            echo "$_SERVER:$_PORT is not running after $_COUNTER seconds."
            sleep 1
        fi
        _COUNTER=$((_COUNTER + 1))
    done
    echo "Error: $_SERVER:$_PORT did not start in time. Rebooting container."
    exit 1
}

load_secret() {
    _SECRET_NAME="$1"
    _ENV_VAR="$2"
    _SECRET_DIR="${MIGASFREE_SECRET_DIR:-/run/secrets}"
    _SECRET_FILE="${_SECRET_DIR}/${_SECRET_NAME}"

    if [ -f "$_SECRET_FILE" ]
    then
        export "$_ENV_VAR"="$(cat "$_SECRET_FILE")"
        return 0
    fi
    return 1
}

show_banner() {
    _SERVICE_INFO="$1"
    _SERVICE_NAME="${2:-$SERVICE}"
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

        $_SERVICE_NAME ($TAG)
        ${_SERVICE_INFO}
        Container: $(hostname)
        Time zone: $(date +%Z) $(date)
        Processes: $(nproc)
"
}

# ==========================================
# Healthcheck Helpers
# ==========================================

check_http() {
    _URL="$1"
    _TIMEOUT="${2:-3}"
    curl -sf --max-time "$_TIMEOUT" "$_URL" > /dev/null 2>&1
}

check_tcp() {
    _HOST="$1"
    _PORT="$2"
    _TIMEOUT="${3:-1}"
    nc -z -w "$_TIMEOUT" "$_HOST" "$_PORT" > /dev/null 2>&1
}

# ==========================================
# Logging Helpers
# ==========================================

log_info() {
    echo "[INFO] $*"
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_success() {
    echo "[OK] $*"
}

check_celery_worker() {
    _BROKER_URL="$1"
    _HOSTNAME="${2:-$(hostname)}"
    _TIMEOUT="${3:-5}"
    
    # shellcheck source=/dev/null
    . /venv/bin/activate
    timeout "$_TIMEOUT" celery -b "${_BROKER_URL}" inspect ping -d "celery@${_HOSTNAME}" > /dev/null 2>&1
}

send_message() {
    _MESSAGE="$1"
    _SERVER="${2:-manager}"
    _DATA="{\"text\":\"$_MESSAGE\", \"service\":\"$SERVICE\", \"node\":\"$NODE\", \"container\":\"$(hostname)\"}"
    curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 --max-time 5 \
        -d "$_DATA" -H "Content-Type: application/json" \
        -X POST "http://${_SERVER}:8080/v1/internal/message" > /dev/null 2>&1 || :
}

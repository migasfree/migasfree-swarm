#!/bin/sh
set -e

. /usr/bin/common.sh

start_message
set_tz

send_message "waiting datastore"
wait_for_service "$REDIS_HOST" "$REDIS_PORT"

REDISINSIGHT_VERSION=$(sed -n 's/.*"version": "\([^"]*\)".*/\1/p' /usr/src/app/redisinsight/api/dist/package.json)
show_banner "redisinsight $REDISINSIGHT_VERSION"

mkdir -p /data || :
chown -R node:node /data || :

if [ -n "$RI_APP_FOLDER_ABSOLUTE_PATH" ]; then
    mkdir -p "$RI_APP_FOLDER_ABSOLUTE_PATH" || :
    chown -R node:node "$RI_APP_FOLDER_ABSOLUTE_PATH" || :
fi

send_message ""

/usr/bin/add_connection &
exec su node -c "cd /usr/src/app && node redisinsight/api/dist/src/main"


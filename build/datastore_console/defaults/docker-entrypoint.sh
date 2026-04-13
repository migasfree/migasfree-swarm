#!/bin/sh
set -e

. /usr/bin/common.sh

start_message
set_tz

send_message "waiting datastore"
wait_for_service "$REDIS_HOST" "$REDIS_PORT"

REDISINSIGHT_VERSION=$(sed -n 's/.*"version": "\([^"]*\)".*/\1/p' /usr/src/app/redisinsight/api/dist/package.json)
show_banner "redisinsight $REDISINSIGHT_VERSION"

send_message ""

su node -c "/usr/bin/add_connection" &
su node -c "cd /usr/src/app; node redisinsight/api/dist/src/main"

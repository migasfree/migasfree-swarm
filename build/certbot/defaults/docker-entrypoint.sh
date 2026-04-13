#!/bin/sh
trap exit TERM

. /usr/bin/common.sh
set_tz
start_message

update-ca-certificates

show_banner

send_message ""

while :;
do
    send_message "renew certificate letsencrypt"
    [ "${HTTPSMODE}" = "auto" ] && . /usr/bin/renew-certificates.sh
    send_message ""
    sleep 12h & wait ${!}
done

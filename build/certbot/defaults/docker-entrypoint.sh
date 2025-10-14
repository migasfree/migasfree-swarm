#!/bin/sh
trap exit TERM

#export MIGASFREE_CERTIFICATES_DIR=/etc/certificates
#mkdir -p $(dirname ${MIGASFREE_CERTIFICATES_DIR})
#ln -s /mnt/datashare/certificates ${MIGASFREE_CERTIFICATES_DIR}

update-ca-certificates

send_message "init certbot"

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
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

send_message ""

while :;
do
    send_message "renew certificate letsencrypt"
    [ "${HTTPSMODE}" = "auto" ] && . /usr/bin/renew-certificates.sh
    send_message ""
    sleep 12h & wait ${!}
done

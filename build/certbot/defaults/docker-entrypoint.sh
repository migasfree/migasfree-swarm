#!/bin/sh
trap exit TERM

#export MIGASFREE_CERTIFICATES_DIR=/etc/certificates
#mkdir -p $(dirname ${MIGASFREE_CERTIFICATES_DIR})
#ln -s /mnt/datashare/certificates ${MIGASFREE_CERTIFICATES_DIR}


send_message "init certbot"

echo "


                   ●                          ●●
                                             ●
         ●●● ●●    ●    ●●     ●●●     ●●●  ●●●●  ●●●  ●●●    ●●●
        ●   ●  ●   ●   ●  ●       ●   ●      ●   ●    ●   ●  ●   ●
        ●   ●  ●   ●   ●  ●    ●●●●    ●●    ●   ●    ●●●●   ●●●●
        ●   ●  ●   ●   ●  ●   ●   ●      ●   ●   ●    ●      ●
        ●   ●  ●   ●    ●●●    ●●●    ●●●    ●   ●     ●●●    ●●●
                          ●
                        ●●

        $SERVICE ($TAG)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

send_message ""
reload_proxy

while :;
do
    send_message "renew certificate letsencrypt" 
    [ "${HTTPSMODE}" = "auto" ] && . /usr/bin/renew-certificates.sh
    send_message ""
    sleep 12h & wait ${!}
done

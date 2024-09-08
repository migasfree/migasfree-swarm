#!/bin/bash
set -e

. /venv/bin/activate


export MIGASFREE_CONF_DIR=/var/lib/migasfree-backend/conf
mkdir -p $(dirname ${MIGASFREE_CONF_DIR})
ln -s ${DATASHARE_MOUNT_PATH}/conf ${MIGASFREE_CONF_DIR}

#export MIGASFREE_CERTIFICATES_DIR=/usr/local/etc/haproxy/certificates
#mkdir -p $(dirname ${MIGASFREE_CERTIFICATES_DIR})
#ln -s ${DATASHARE_MOUNT_PATH}/certificates ${MIGASFREE_CERTIFICATES_DIR}
#mkdir -p /usr/local/etc/haproxy/certificates


# If not certificate, haproxy don't start and/or certbot can't challenge complete
# Create a self-certificate to init
#[ ! -f "/usr/local/etc/haproxy/certificates/${FQDN}.pem" ] && \
#  {
#    echo "INFO: Creating self certificates..."
#    install-certs
#  }

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]
then
    set -- haproxy "$@"
fi




# services page
# =============
cd /usr/share/services/
python3 services.py 8001 &
cd -

message "Initial configuration"

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

        migasfree PROXY
        $(haproxy -v | head -1)
        Container: $HOSTNAME
        Time zome: $TZ $(date)
        Processes: $(nproc)

"

# load proxy
# =============
mkdir -p /var/run/haproxy/

message ""

haproxy -W -db -S /var/run/haproxy/haproxy-master-socket -f /etc/haproxy/haproxy.cfg \
    -p /var/run/haproxy/haproxy.pid

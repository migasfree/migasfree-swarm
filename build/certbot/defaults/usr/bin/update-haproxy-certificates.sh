#!/bin/sh

for ip in $(getent hosts proxy | awk '{ print $1 }'); do
    # Start transaction
    echo -e "set ssl cert /mnt/cluster/certificates/${STACK}/server/${FQDN}.pem <<\n$(cat /etc/certificates/${STACK}.pem)\n" | socat tcp4-connect:$ip:9999 -

    # Commit transaction
    echo "commit ssl cert /mnt/cluster/certificates/${STACK}/server/${FQDN}.pem" | socat tcp4-connect:$ip:9999 -

    # Show certification info (not essential)
    echo "show ssl cert /mnt/cluster/certificates/${STACK}/server/${FQDN}.pem" | socat tcp4-connect:$ip:9999 -
done

#!/bin/sh

# Start transaction
echo -e "set ssl cert /usr/local/etc/haproxy/certificates/${STACK}.pem <<\n$(cat /etc/certificates/${STACK}.pem)\n" | socat tcp-connect:proxy_proxy:9999 -

# Commit transaction
echo "commit ssl cert /usr/local/etc/haproxy/certificates/${STACK}.pem" | socat tcp-connect:proxy_proxy:9999 -

# Show certification info (not essential)
echo "show ssl cert /usr/local/etc/haproxy/certificates/${STACK}.pem" | socat tcp-connect:proxy_proxy:9999 -

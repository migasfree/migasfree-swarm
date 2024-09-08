FROM certbot/certbot

# Install socat
RUN apk update && apk add socat

# Copy scripts
COPY defaults/usr/bin/* /usr/bin/
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

# Expose port 380
EXPOSE 380


ENTRYPOINT ["/docker-entrypoint.sh"]
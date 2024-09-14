FROM certbot/certbot:latest

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

# Install socat
RUN apk upgrade --no-cache && \
    apk update && apk add socat

# Copy scripts
COPY defaults/usr/bin/* /usr/bin/
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

# Expose port 380
EXPOSE 380


ENTRYPOINT ["/docker-entrypoint.sh"]
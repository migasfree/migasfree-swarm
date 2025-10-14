FROM certbot/certbot:v5.0.0 AS origen

# To remove volumes
FROM scratch

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY --from=origen / /

COPY VERSION /VERSION

# Install socat
RUN apk upgrade --no-cache && \
    apk update && apk add socat curl

# Copy scripts
COPY defaults/usr/bin/* /usr/bin/
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

# Expose port 380
EXPOSE 380


ENTRYPOINT ["/docker-entrypoint.sh"]
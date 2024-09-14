# https://hub.docker.com/_/redis/
FROM redis:alpine3.20
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk --no-cache upgrade && \
    apk add coreutils curl tzdata

COPY defaults/docker-entrypoint.sh  /usr/local/bin/
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 6379

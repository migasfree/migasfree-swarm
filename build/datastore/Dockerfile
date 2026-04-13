# https://hub.docker.com/_/redis/
FROM redis:8.2-alpine3.22
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk --no-cache upgrade && \
    apk add coreutils curl tzdata

COPY defaults/docker-entrypoint.sh  /usr/local/bin/
COPY defaults/usr/bin /usr/bin

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 6379

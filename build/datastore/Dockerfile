# https://hub.docker.com/_/redis/
FROM redis:6.2.5-alpine
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

RUN apk add coreutils curl tzdata

COPY defaults/docker-entrypoint.sh  /usr/local/bin/
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 6379

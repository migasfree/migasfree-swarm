#FROM postgres:13.2-alpine
FROM postgres:alpine3.19
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk add curl coreutils apk-cron musl-locales

COPY defaults/usr /usr
COPY defaults/etc /etc
COPY defaults/docker-entrypoint-extend.sh /docker-entrypoint-extend.sh

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint-extend.sh"]

FROM alpine:3.20

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"


ARG TAG=latest

ENV TAG=${TAG} \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apk upgrade --no-cache && \
    apk add --no-cache pgpool postgresql-client bash curl bind-tools jq tzdata musl-locales

COPY defaults/etc/pgpool2 /etc/pgpool
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/healthcheck.sh /healthcheck.sh

RUN chmod +x /docker-entrypoint.sh /healthcheck.sh

HEALTHCHECK --start-period=30s --interval=30s --timeout=5s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]

# https://ilhicas.com/2018/04/07/Haproxy-ssl-termination-jekyll.html
FROM haproxy:lts-alpine3.21 AS builder
# WARNING !!! BUG with haproxy:lts-alpine3.22  (haproxy 3.2.5)
# ./migasfree-swarm deploy -> /services/status -> disconnected

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

USER root

ARG TAG=latest

COPY VERSION /VERSION

ENV TAG=${TAG} \
    LIVE_CERT_FOLDER="/etc/letsencrypt/live" \
    BUILD_DEPENDS='py3-pip' \
    RUNTIME_DEPENDS='bash tzdata inotify-tools openssl ca-certificates socat curl bind-tools python3 py3-virtualenv curl cronie' \
    RUNTIME_PIP='web.py jinja2 dnspython requests'

RUN apk upgrade --no-cache && \
    apk add --update --no-cache $BUILD_DEPENDS $RUNTIME_DEPENDS && \
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir $RUNTIME_PIP && \
    apk del $BUILD_DEPENDS && \
    rm -rf /var/cache/apk/*

COPY defaults/usr/share /usr/share
COPY defaults/usr/bin /usr/bin
COPY defaults/etc /etc
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]

# https://ilhicas.com/2018/04/07/Haproxy-ssl-termination-jekyll.html
FROM haproxy:lts-alpine3.22 AS builder

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

COPY VERSION /VERSION

ENV TAG=${TAG} \
    LIVE_CERT_FOLDER="/etc/letsencrypt/live" \
    BUILD_DEPENDS='py3-pip' \
    RUNTIME_DEPENDS='bash tzdata inotify-tools openssl ca-certificates socat curl bind-tools python3 py3-virtualenv curl' \
    RUNTIME_PIP='jinja2'

USER root
RUN apk upgrade --no-cache && \
    apk add --update --no-cache $BUILD_DEPENDS $RUNTIME_DEPENDS && \
    mkdir /usr/share/proxy && \
    cd /usr/share/proxy && \
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir $RUNTIME_PIP && \
    apk del $BUILD_DEPENDS && \
    rm -rf /var/cache/apk/*

COPY defaults/usr /usr
COPY defaults/etc /etc
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/usr/bin /usr/bin
HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

RUN mkdir -p /var/run/haproxy /usr/local/etc/haproxy && \
    chown -R haproxy:haproxy /var/run/haproxy /usr/local/etc/haproxy /usr/share/proxy /venv

# USER haproxy

ENTRYPOINT ["/docker-entrypoint.sh"]

FROM alpine:3.22
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

# https://docker-py.readthedocs.io/en/stable/plugins.html

ARG TAG=latest \
    BUILD_DEPENDS='py3-pip' \
    RUNTIME_DEPENDS='python3 py3-virtualenv ca-certificates openssl docker docker-cli-compose tzdata curl'  \
    RUNTIME_PIP='docker packaging jinja2 requests cryptography'

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk upgrade --no-cache && \
    apk add --update --no-cache $BUILD_DEPENDS $RUNTIME_DEPENDS && \
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir $RUNTIME_PIP && \
    apk del $BUILD_DEPENDS && \
    rm -rf /var/cache/apk/*

COPY defaults/usr/bin /usr/bin
COPY defaults/tools /tools
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

RUN sed -i "s/@@TAG@@/$TAG/g" /tools/migasfree-swarm

ENTRYPOINT ["/docker-entrypoint.sh"]

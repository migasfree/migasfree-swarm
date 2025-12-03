ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM alpine:3.22
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

COPY VERSION /VERSION

ENV TAG=${TAG} \
    TERM=xterm \
    USER=root \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LANG=C.UTF-8 \
    _UID=890 \
    _GID=890

RUN _BUILD_DEPENDS='python3-dev py3-setuptools py3-pip wget gcc musl-dev libffi-dev' && \
    _DEPENDS='gnupg apk-tools alpine-sdk gzip python3 py3-virtualenv netcat-openbsd curl tzdata bash' && \
    _PIP_DEPENDS='requests celery[redis]' && \
    addgroup -g $_GID www-data || : && \
    adduser -D -u $_UID -G www-data -s /bin/bash www-data && \
    apk update && \
    apk upgrade && \
    apk add --no-cache $_DEPENDS && \
    apk add --no-cache $_BUILD_DEPENDS && \
    python3 -m venv /venv && \
    . /venv/bin/activate  && \
    pip3 install --no-cache-dir $_PIP_DEPENDS && \
    mkdir /pms && \
    apk del $_BUILD_DEPENDS && \
    rm -rf /var/cache/apk/*

COPY --from=core /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

RUN chown -R $_UID:$_GID /pms

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

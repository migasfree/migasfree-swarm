ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM debian:13-slim
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

COPY VERSION /VERSION

ENV TAG=${TAG} \
    TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    USER=root \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LANG=C.UTF-8 \
    _UID=890 \
    _GID=890

RUN _BUILD_DEPENDS='python3-setuptools python3-pip wget' && \
    _DEPENDS='gnupg dpkg-dev gzip python3 python3-venv netcat-openbsd curl apt-utils tzdata' && \
    _PIP_DEPENDS='requests celery[redis]' && \
    usermod -u $_UID www-data && \
    groupmod -g $_GID www-data && \
    chsh -s /bin/bash www-data && \
    apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends  $_DEPENDS && \
    apt-get install -y --no-install-recommends  $_BUILD_DEPENDS && \
    python3 -m venv /venv && \
    . /venv/bin/activate  && \
    pip3 install $_PIP_DEPENDS && \
    mkdir /pms && \
    apt-get -y purge $_BUILD_DEPENDS && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=core /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

RUN chown -R $_UID:$_GID /pms

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

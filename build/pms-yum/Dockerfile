ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM fedora:42
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
    _GID=890 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production

RUN _BUILD_DEPENDS='python3-pip wget' && \
    _DEPENDS='gnupg createrepo gzip python3 python3-virtualenv netcat util-linux-user' && \
    _PIP_DEPENDS='requests celery[redis] setuptools' && \
    useradd www-data && \
    usermod -u $_UID www-data && \
    groupmod -g $_GID www-data && \
    #lchsh -s /bin/bash www-data && \
    yum -y update && \
    yum -y install $_DEPENDS && \
    yum -y install $_BUILD_DEPENDS && \
    pip3 install $_PIP_DEPENDS && \
    virtualenv /venv && \
    mkdir /pms && \
    yum -y remove $_BUILD_DEPENDS && \
    yum -y  clean all

COPY --from=core /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

RUN chown -R $_UID:$_GID /pms

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

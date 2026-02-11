ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM archlinux/archlinux:base-20260211.0.489484
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

COPY VERSION /VERSION

ENV TAG=${TAG} \
    TERM=xterm \
    USER=root \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    _UID=890 \
    _GID=890 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production

RUN _BUILD_DEPENDS='python-setuptools python-pip wget' && \
    _DEPENDS='gnupg gzip python python-virtualenv curl openbsd-netcat python-dateutil' && \
    _PIP_DEPENDS='celery redis requests' && \
    groupadd -g $_GID www-data && \
    useradd -u $_UID -g www-data -s /bin/bash www-data && \
    pacman-key --init && \
    pacman-key --populate archlinux && \
    pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Syu --noconfirm && \
    pacman --noconfirm --sync $_DEPENDS $_BUILD_DEPENDS && \
    virtualenv /venv && \
    /venv/bin/pip install --break-system-packages $_PIP_DEPENDS && \
    mkdir /pms && \
    rm -rf /var/tmp/* /usr/share/man/* /var/cache/pacman/pkg/* /var/lib/pacman/sync/*

COPY --from=core /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

RUN chown -R $_UID:$_GID /pms

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

FROM archlinux:base-20240101.0.204074
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

COPY VERSION /VERSION

ENV TERM=xterm \
    USER=root \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LC_CTYPE=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    _UID=890 \
    _GID=890 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production 

RUN _TAG=$(cat /VERSION) && \
    _BUILD_DEPENDS='python-setuptools python-pip wget' && \
    _DEPENDS='gnupg gzip python3 python-virtualenv curl netcat python-requests python-redis python-celery python-dateutil' && \
#    _PIP_DEPENDS='' && \
    useradd www-data &&\
    usermod -u $_UID www-data && \
    groupmod -g $_GID www-data && \
    chsh -s /bin/bash www-data  && \
    pacman -Sy  && \
    pacman --noconfirm --sync  $_DEPENDS  && \
    pacman --noconfirm --sync  $_BUILD_DEPENDS && \
#    pip install $_PIP_DEPENDS && \
    virtualenv /venv && \
    mkdir /pms && \
    rm -rf /var/tmp/* /usr/share/man/* /var/cache/pacman/pkg/* /var/lib/pacman/sync/*

COPY --from=migasfree/core:5.0-beta /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

RUN chown -R $_UID:$_GID /pms

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

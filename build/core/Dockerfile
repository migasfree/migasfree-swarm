FROM debian:stable-slim AS builder
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY /VERSION /VERSION

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    USER=root \
    LANG=en_US.UTF-8 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production \
    PYTHONPATH=/venv/lib/python3.11/site-packages \
    _UID=890 \
    _GID=890 \
    _BUILD_DEPENDS='git python3-dev python3-all python3-all-dev unzip g++ gcc-12 libcairo2-dev libjpeg62-turbo-dev libxml2-dev libxslt1-dev libpq-dev' \
    _DEPENDS='procps libzmq5 gnupg rng-tools curl apt-utils bzip2 xz-utils python3 python3-venv python3-minimal python3-pip p7zip-full vim wget postgresql-client netcat-traditional libmagic1' \
    _PIP_DEPENDS='uvicorn[standard]==0.18.3'

RUN apt update && \
    apt dist-upgrade -y && \
    apt install -y --no-install-recommends apt-utils && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "es_ES.UTF-8 UTF-8" >> /etc/locale.gen && \
    apt install -y --no-install-recommends locales && \
    dpkg-reconfigure locales && \
    update-locale LANG=$LANG && \
    apt install -y --no-install-recommends chrony && \
    apt install -y --no-install-recommends $_BUILD_DEPENDS  && \
    apt install -y --no-install-recommends $_DEPENDS && \
    python3 -m venv /venv && \
    . /venv/bin/activate  && \
    pip install --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade setuptools wheel 

RUN apt-get install -y swig 

RUN cd / && \
    . /venv/bin/activate && \
    git clone https://github.com/migasfree/migasfree-backend && \
    cd /migasfree-backend && \
    git checkout $(cat /VERSION)

RUN  cd / && \
    . /venv/bin/activate && \
    cd /migasfree-backend && \
    pip install --no-cache-dir -r requirements/production.txt && \
    pip install --no-cache-dir requests_toolbelt && \
    python3 setup.py install && \
    rm -rf /migasfree-backend 

RUN cd / && \
    . /venv/bin/activate && \
    pip3 install --no-cache-dir uvicorn[standard]==0.22.0

RUN . /venv/bin/activate && \
    # Symbolic links to be copied from other containers && \
    # MIGASFREE MODULE && \
    MIGASFREE_MODULE_PATH=$(python3 -c "import migasfree;print(migasfree.__path__[0])") && \
    ln -s $MIGASFREE_MODULE_PATH /migasfree && \
    # STATIC FILES && \
    mkdir /static && \
    STATIC_DJANGO=$(python3 -c "import django;print(django.__path__[0])") && \
    ln -s ${STATIC_DJANGO}/contrib/admin/static/admin /static/admin && \
    STATIC_REST_FRAMEWORK=$(python3 -c "import rest_framework;print(rest_framework.__path__[0])") && \
    ln -s ${STATIC_REST_FRAMEWORK}/static/rest_framework /static/rest_framework && \
    STATIC_DRF_YASG=$(python3 -c "import drf_yasg;print(drf_yasg.__path__[0])") && \
    ln -s ${STATIC_DRF_YASG}/static/drf-yasg /static/drf-yasg

# explicity set user/group IDs to www-data && \
RUN usermod -u $_UID www-data && \
    groupmod -g $_GID www-data && \
    chsh -s /bin/bash www-data && \
    #. /venv/bin/activate &&\
    #django-admin collectstatic --noinput && \
    apt -y --auto-remove purge $_BUILD_DEPENDS && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/pip_build_root && \
    rm -rf /root/.cache

COPY defaults/usr /usr
COPY defaults/default_settings.py /default_settings.py
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

FROM scratch
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY /VERSION /VERSION

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    USER=root \
    LANG=en_US.UTF-8 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production \
    PYTHONPATH=/venv/lib/python3.11/site-packages \
    _UID=890 \
    _GID=890

COPY --from=builder / /

COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]
EXPOSE 80

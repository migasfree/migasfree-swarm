FROM debian:13-slim AS builder
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest
ENV TAG=${TAG}

COPY /VERSION /VERSION

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    USER=root \
    LANG=en_US.UTF-8 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production \
    PYTHONPATH=/venv/lib/python3.13/site-packages \
    _UID=890 \
    _GID=890 \
    _BUILD_DEPENDS='git swig python3-dev python3-all python3-all-dev unzip g++ gcc-12 libcairo2-dev libjpeg62-turbo-dev libxml2-dev libxslt1-dev libpq-dev' \
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
    python3 -m pip install --no-cache-dir --upgrade setuptools wheel && \
    find /venv -name "__pycache__" -type d -exec rm -rf {} +

RUN git clone --depth 1 --branch $(cat /VERSION) https://github.com/migasfree/migasfree-backend /migasfree-backend

RUN . /venv/bin/activate && \
    cd /migasfree-backend && \
    pip install --no-cache-dir requests_toolbelt && \
    pip install --no-cache-dir . && \
    rm -rf /migasfree-backend

RUN . /venv/bin/activate && \
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
    STATIC_DRF_SPECTACULAR_SIDECAR=$(python3 -c "import drf_spectacular_sidecar;print(drf_spectacular_sidecar.__path__[0])") && \
    ln -s ${STATIC_DRF_SPECTACULAR_SIDECAR}/static/drf_spectacular_sidecar /static/drf_spectacular_sidecar

# Build the final image
FROM debian:13-slim
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest
ENV TAG=${TAG}

COPY /VERSION /VERSION

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production \
    PYTHONPATH=/venv/lib/python3.13/site-packages \
    _UID=890 \
    _GID=890

# Runtime dependencies
RUN apt update && \
    apt install -y --no-install-recommends \
    procps \
    libzmq5 \
    ca-certificates \
    curl \
    python3 \
    postgresql-client \
    netcat-traditional \
    libmagic1 \
    locales && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "es_ES.UTF-8 UTF-8" >> /etc/locale.gen && \
    dpkg-reconfigure locales && \
    update-locale LANG=$LANG && \
    rm -rf /var/lib/apt/lists/*

# Explicity set user/group IDs to www-data
RUN usermod -u $_UID www-data && \
    groupmod -g $_GID www-data && \
    chsh -s /bin/bash www-data

# Atomic copies from builder with ownership set (prevents layer duplication)
COPY --from=builder --chown=$_UID:$_GID /venv /venv
COPY --from=builder --chown=$_UID:$_GID /static /static

# Recreate symlinks (avoid copying content if they were followed in previous steps)
RUN ln -s /venv/lib/python3.13/site-packages/migasfree /migasfree && \
    chown -h www-data:www-data /migasfree

COPY --chown=$_UID:$_GID defaults/usr /usr
COPY --chown=$_UID:$_GID defaults/default_settings.py /default_settings.py
COPY --chown=$_UID:$_GID defaults/docker-entrypoint.sh /docker-entrypoint.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]
EXPOSE 80

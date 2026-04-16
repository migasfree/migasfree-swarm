ARG TAG=latest
FROM migasfree/core:${TAG} AS core

# Stage 1: Builder
FROM archlinux/archlinux:base-20260211.0.489484 AS builder
RUN pacman -Syu --noconfirm python-pip python-virtualenv python-setuptools wget gcc binutils
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /venv/bin/pip install --no-cache-dir celery redis requests && \
    find /venv -name "__pycache__" -type d -exec rm -rf {} +

# Stage 2: Final
FROM archlinux/archlinux:base-20260211.0.489484
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest
ENV TAG=${TAG} \
    TERM=xterm \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    _UID=890 \
    _GID=890 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production \
    PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1

# Setup locales and runtime dependencies
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    pacman-key --init && \
    pacman-key --populate archlinux && \
    pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Syu --noconfirm && \
    _DEPENDS='gnupg gzip python curl openbsd-netcat python-dateutil inetutils' && \
    pacman -S --noconfirm $_DEPENDS && \
    getent group www-data || groupadd -g $_GID www-data && \
    getent passwd www-data || useradd -u $_UID -g www-data -s /bin/bash www-data && \
    mkdir -p /pms && \
    rm -rf /var/cache/pacman/pkg/* /var/lib/pacman/sync/*

# Atomic copies from builders
COPY --from=builder --chown=$_UID:$_GID /venv /venv
COPY --from=core --chown=$_UID:$_GID /migasfree /pms/migasfree
COPY --chown=$_UID:$_GID defaults/usr/bin /usr/bin
COPY --chown=$_UID:$_GID defaults/docker-entrypoint.sh /docker-entrypoint.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

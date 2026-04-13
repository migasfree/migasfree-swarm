ARG TAG=latest
FROM migasfree/core:${TAG} AS core

# Stage 1: Builder
FROM fedora:42 AS builder
RUN dnf install -y python3-pip python3-virtualenv
RUN virtualenv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /venv/bin/pip install --no-cache-dir requests celery[redis]

# Stage 2: Final
FROM fedora:42
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest
ENV TAG=${TAG} \
    TERM=xterm \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    _UID=890 \
    _GID=890 \
    PATH="/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production

# Runtime dependencies
RUN dnf -y update && \
    dnf -y install --nodocs gnupg createrepo gzip python3 netcat util-linux-user hostname && \
    dnf clean all && \
    getent group www-data || groupadd -g $_GID www-data && \
    getent passwd www-data || useradd -u $_UID -g www-data -s /bin/bash www-data

# Atomic copies
COPY --from=builder /venv /venv
COPY --from=core --chown=www-data:www-data /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

RUN chown -R www-data:www-data /venv /pms
# Reverted: let entrypoint handle initialization as root
# USER www-data

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

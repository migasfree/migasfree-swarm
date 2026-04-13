ARG TAG=latest
FROM migasfree/core:${TAG} AS core

# Stage 1: Builder
FROM debian:13-slim AS builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-venv python3-setuptools wget \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /venv/bin/pip install --no-cache-dir requests celery[redis]

# Stage 2: Final
FROM debian:13-slim
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest
ENV TAG=${TAG} \
    TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    _UID=890 \
    _GID=890 \
    PATH="/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg dpkg-dev gzip python3 python3-minimal netcat-openbsd curl apt-utils tzdata \
    && rm -rf /var/lib/apt/lists/* && \
    usermod -u $_UID www-data && \
    groupmod -g $_GID www-data

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

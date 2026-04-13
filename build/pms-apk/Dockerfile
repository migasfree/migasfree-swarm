ARG TAG=latest
FROM migasfree/core:${TAG} AS core

# Stage 1: Builder
FROM alpine:3.22 AS builder
RUN apk add --no-cache python3 py3-pip py3-virtualenv python3-dev gcc musl-dev libffi-dev
RUN python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /venv/bin/pip install --no-cache-dir requests celery[redis]

# Stage 2: Final
FROM alpine:3.22
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest
ENV TAG=${TAG} \
    TERM=xterm \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    _UID=890 \
    _GID=890 \
    PATH="/venv/bin:$PATH"

# Runtime dependencies
RUN apk add --no-cache gnupg apk-tools alpine-sdk gzip python3 py3-virtualenv netcat-openbsd curl tzdata bash && \
    getent group www-data >/dev/null || addgroup -g $_GID www-data && \
    getent passwd www-data >/dev/null || adduser -D -u $_UID -G www-data -s /bin/bash www-data

# Atomic copies
COPY --from=builder /venv /venv
COPY --from=core --chown=www-data:www-data /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

RUN chown -R www-data:www-data /venv /pms
# USER www-data

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

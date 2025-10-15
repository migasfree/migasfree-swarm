FROM python:3.13-slim

ARG TAG=latest

LABEL maintainer="alberto@migasfree.org"
LABEL description="MCP server for Migasfree"
LABEL version="1.0.0"


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    MCP_PORT=8080 \
    MCP_HOST=0.0.0.0 \
    LOG_LEVEL=INFO \
    HF_HOME=/app/model_cache \
    XDG_CACHE_HOME=/app/model_cache

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y postgresql-client curl ca-certificates sudo && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    groupadd -r -g 890 mcpuser && useradd -r -u 890 -g mcpuser mcpuser && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/model_cache && \
    chown -R mcpuser:mcpuser /app/model_cache


COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/app /app
COPY defaults/usr/bin /usr/bin

RUN chown -R mcpuser:mcpuser /app && \
    echo "mcpuser ALL=(ALL) NOPASSWD: /usr/sbin/update-ca-certificates" >> /etc/sudoers

USER mcpuser

EXPOSE 8080

COPY defaults/healthcheck.sh /healthcheck.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
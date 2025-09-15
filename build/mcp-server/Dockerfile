FROM python:3.13-slim

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

RUN chown -R mcpuser:mcpuser /app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -s -I http://localhost:8080/openapi.json | head -n 1 | grep -q "200 OK" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
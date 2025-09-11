# Dockerfile
FROM python:3.11-slim

# Metadatos
LABEL maintainer="alberto@migasfree.org"
LABEL description="Servidor MCP for Migasfree"
LABEL version="1.0.0"

# Variables de entorno
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

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y postgresql-client curl  && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    groupadd -r -g 890 mcpuser && useradd -r -u 890 -g mcpuser mcpuser && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/model_cache && \
    #python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('embaas/sentence-transformers-multilingual-e5-large', cache_folder='/app/model_cache')" && \
    chown -R mcpuser:mcpuser /app/model_cache


COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/app /app
RUN chown -R mcpuser:mcpuser /app

# Cambiar a usuario no-root
USER mcpuser

# Exponer puerto HTTP
EXPOSE 8080

# Health check HTTP
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -s -I http://localhost:8080/openapi.json | head -n 1 | grep -q "200 OK" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
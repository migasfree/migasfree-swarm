FROM python:3.13-slim AS builder

ARG TAG=latest

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"
LABEL description="TDA (Topological Data Analysis) analytics worker for Migasfree"
LABEL version="${TAG}"

ENV TAG=${TAG} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /build

COPY requirements.txt .

# Build dependencies for native extensions (numpy, scipy, giotto-tda)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential cmake gfortran && \
    rm -rf /var/lib/apt/lists/*


# --- Final image ---
FROM python:3.13-slim

ARG TAG=latest

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"
LABEL description="TDA (Topological Data Analysis) analytics worker for Migasfree"

ENV TAG=${TAG} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

COPY VERSION /VERSION

# Runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libopenblas0 \
    liblapack3 \
    libgomp1 \
    postgresql-client \
    gosu \
    netcat-openbsd \
    procps && \
    rm -rf /var/lib/apt/lists/* && \
    getent group tdauser || groupadd -r -g 890 tdauser && \
    getent passwd tdauser || useradd -r -u 890 -g tdauser tdauser && \
    mkdir -p /app /data/tda && \
    chown -R tdauser:tdauser /app /data/tda

# Python packages from builder stage
COPY --from=builder /install /usr/local

WORKDIR /app

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/app /app
COPY defaults/usr/bin /usr/bin

RUN chmod +x /docker-entrypoint.sh && \
    chown -R tdauser:tdauser /app

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]

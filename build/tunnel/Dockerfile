FROM python:3.14-slim

WORKDIR /usr/share/tunnel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt -y update && \
    apt install -y curl netcat-openbsd

COPY defaults/usr /usr
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]

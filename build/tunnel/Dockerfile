FROM python:3.13-slim

ARG TAG=latest

ENV TAG=${TAG}

WORKDIR /usr/share/tunnel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt -y update && \
    apt install -y curl netcat-openbsd gosu

COPY defaults/usr /usr
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

RUN getent group migasfree || groupadd -g 890 migasfree && \
    getent passwd migasfree || useradd -u 890 -g migasfree -s /bin/bash -m migasfree

# USER migasfree

ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]

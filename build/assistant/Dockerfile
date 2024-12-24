FROM alpine:3.21

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk upgrade --no-cache && \
    apk add --no-cache tzdata py-pip nano curl && \
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir -q -U google-generativeai web.py psycopg2-binary requests

COPY defaults/docker-entrypoint.sh /
COPY defaults/usr/ /usr
COPY defaults/www /www
COPY defaults/etc /etc

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=5s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]
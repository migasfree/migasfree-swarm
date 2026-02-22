FROM python:3.13-alpine3.22

ARG TAG=latest

ENV TAG=${TAG} \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /usr/share/manager

COPY ./requirements.txt /usr/share/manager/requirements.txt

RUN apk add --no-cache openssl curl cronie socat openssh-client libpq tzdata musl-locales && \
    apk add --no-cache --virtual .build-deps postgresql-dev gcc musl-dev && \
    pip install --no-cache-dir --upgrade -r /usr/share/manager/requirements.txt && \
    apk del .build-deps

COPY ./defaults/ /

EXPOSE 8080

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

CMD ["/docker-entrypoint.sh"]

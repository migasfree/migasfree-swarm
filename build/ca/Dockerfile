FROM python:3.14-alpine3.22

ENV FQDN=inv.org
ENV INV=inv
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/share/ca-service

COPY ./requirements.txt /usr/share/ca-service/requirements.txt

RUN apk update && \
    apk add tar openssl haveged curl cronie socat && \
    pip install --no-cache-dir --upgrade -r /usr/share/ca-service/requirements.txt


COPY ./defaults/ /


EXPOSE 80

CMD ["/docker-entrypoint.sh"]

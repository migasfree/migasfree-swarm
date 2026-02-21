FROM alpine:3.20

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

RUN apk upgrade --no-cache && \
    apk add --no-cache pgpool postgresql-client bash curl

COPY defaults/etc/pgpool2 /etc/pgpool
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

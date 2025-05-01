
FROM filebrowser/filebrowser:v2.32.0
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG} \
    RUNTIME_DEPENDS='tzdata'

COPY VERSION /VERSION

RUN apk --no-cache upgrade && \
    apk add --update --no-cache $RUNTIME_DEPENDS

COPY defaults/etc /etc
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=5s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
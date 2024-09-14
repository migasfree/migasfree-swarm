FROM redis/redisinsight:2.56
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

ENV RUNTIME_DEPENDS="tzdata curl"

USER root

RUN apk --no-cache upgrade && \
    apk add --update --no-cache $RUNTIME_DEPENDS && \
    # explicity set uid/gid (890) to user node
    sed -i "s/node:x:[0-9]\+:[0-9]\+:/node:x:890:890:/" /etc/passwd && \
    sed -i "s/node:x:[0-9]\+:/node:x:890:/" /etc/group 

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh

HEALTHCHECK --start-period=2s --interval=5s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
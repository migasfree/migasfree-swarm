FROM dpage/pgadmin4:9.11
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

# https://github.com/pgadmin-org/pgadmin4/blob/master/docs/en_US/container_deployment.rst

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

ENV RUNTIME_DEPENDS='tzdata curl su-exec'

USER root
RUN apk --no-cache upgrade && \
    apk add --update --no-cache $RUNTIME_DEPENDS && \
    # explicity set uid/gid (890) to user pgadmin
    sed -i "s/pgadmin:x:[0-9]\+:/pgadmin:x:890:/" /etc/passwd && \
    sed -i "s/pgadmin:x:[0-9]\+:/pgadmin:x:890:/" /etc/group

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/entrypoint.sh /entrypoint.sh

COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
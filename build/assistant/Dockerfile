FROM ghcr.io/open-webui/open-webui:v0.6.15
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG} \
    RUNTIME_DEPENDS='tzdata'

COPY VERSION /VERSION

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/usr /usr


ENTRYPOINT ["/docker-entrypoint.sh"]
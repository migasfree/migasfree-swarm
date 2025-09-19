FROM ghcr.io/open-webui/open-webui:0.6.28-slim

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG} \
    RUNTIME_DEPENDS='tzdata' \
    USE_EMBEDDING_MODEL_DOCKER=''

COPY VERSION /VERSION

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/usr /usr


ENTRYPOINT ["/docker-entrypoint.sh"]
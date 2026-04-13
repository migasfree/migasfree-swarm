FROM filebrowser/filebrowser:v2.46.1 AS base

FROM alpine:3.22

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG} \
    RUNTIME_DEPENDS='tzdata curl'

COPY VERSION /VERSION

RUN apk --no-cache upgrade && \
    apk add --update --no-cache $RUNTIME_DEPENDS

COPY defaults/etc /etc
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

COPY defaults/usr/bin /usr/bin

# Define non-root user UID and GID
ENV UID=890
ENV GID=890

# Create user group and user
RUN addgroup -g $GID user && \
    adduser -D -u $UID -G user user

COPY --from=base /bin/filebrowser /bin/filebrowser
COPY --from=base /JSON.sh /JSON.sh

# Create data directories, set ownership, and ensure healthcheck script is executable
RUN mkdir -p /config /database /srv
RUN chown -R user:user /config /database /srv

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

# Reverted: let entrypoint handle user switch after root-only tasks
# USER user

ENTRYPOINT ["/docker-entrypoint.sh"]

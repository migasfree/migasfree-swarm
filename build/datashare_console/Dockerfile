FROM gtstef/filebrowser:1.5.3-stable AS base

FROM alpine:3.22

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG} \
    RUNTIME_DEPENDS='tzdata curl'

COPY VERSION /VERSION

RUN apk --no-cache upgrade && \
    apk add --update --no-cache $RUNTIME_DEPENDS

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/usr/bin /usr/bin

# Define non-root user UID and GID
ENV UID=890
ENV GID=890

# Create user group and user
RUN addgroup -g $GID user && \
    adduser -D -u $UID -G user user

COPY --from=base /home/filebrowser /home/filebrowser
RUN ln -sf /home/filebrowser/filebrowser /bin/filebrowser

# Create data directories, set ownership, and ensure healthcheck script is executable
RUN mkdir -p /config /database /srv /tmp && \
    chown -R user:user /home/filebrowser /config /database /srv /tmp

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]

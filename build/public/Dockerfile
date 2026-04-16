ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM cmoore1776/nginx:1.29.0
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

# change uid and gid for nginx user
RUN apk upgrade --no-cache && \
    apk --no-cache add bind-tools curl shadow tzdata socat && \
    usermod -u 890 nginx && \
    groupmod -g 890 nginx && \
    apk del shadow

COPY --chown=890:890 defaults/var/migasfree /var/migasfree

# STATIC FILES
COPY --from=core --chown=890:890 /static/admin  /var/migasfree/static/admin
COPY --from=core --chown=890:890 /static/drf_spectacular_sidecar /var/migasfree/static/drf_spectacular_sidecar
COPY --from=core --chown=890:890 /static/rest_framework /var/migasfree/static/rest_framework
COPY --chown=890:890 defaults/var/migasfree/static /var/migasfree/static

COPY defaults/usr/bin /usr/bin
COPY defaults/etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1

CMD [""]

# Reverted: let entrypoint handle initialization as root
# USER nginx

ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]

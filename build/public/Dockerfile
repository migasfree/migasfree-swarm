ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM cmoore1776/nginx:1.27.3
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

# change uid and gid for nginx user
RUN apk upgrade --no-cache && \
    apk --no-cache add bind-tools curl shadow tzdata && \
    usermod -u 890 nginx && \
    groupmod -g 890 nginx && \
    apk del shadow

COPY defaults/var/migasfree /var/migasfree

# STATIC FILES
COPY --from=core /static/admin  /var/migasfree/static/admin
COPY --from=core /static/drf_spectacular_sidecar /var/migasfree/static/drf_spectacular_sidecar
COPY --from=core /static/rest_framework /var/migasfree/static/rest_framework
COPY defaults/var/migasfree/static /var/migasfree/static

RUN chown -R 890:890 /var/migasfree/

COPY defaults/usr/bin /usr/bin
COPY defaults/etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh


COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=5s --timeout=3s CMD /healthcheck.sh || exit 1

CMD [""]

ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]


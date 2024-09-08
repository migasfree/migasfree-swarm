#FROM node:18.16.1-alpine3.18 AS build-stage
FROM node:22-alpine AS build-stage
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"
COPY VERSION /VERSION
RUN _TAG=$(cat /VERSION) && \
        apk add git && \
        git clone  https://github.com/migasfree/migasfree-frontend  && \
        cd migasfree-frontend && \
        git checkout $_TAG && \
        echo 'MIGASFREE_SERVER=https://__FQDN__' > /migasfree-frontend/.env

RUN cd migasfree-frontend && \
        cp package*.json /app && \
        yarn global add @quasar/cli && \
        yarn && \
        quasar build

FROM nginx:stable-alpine3.17 AS production-stage
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"
COPY VERSION /VERSION
RUN _TAG=$(cat /VERSION) && \
    apk add curl

# Copy application
COPY --from=build-stage /migasfree-frontend/dist/spa /usr/share/nginx/html
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=5s --timeout=3s CMD /healthcheck.sh || exit 1


COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]

EXPOSE 80

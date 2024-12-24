FROM node:23-alpine3.21 AS build-stage
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk upgrade --no-cache && \
    apk add git && \
    git clone  https://github.com/migasfree/migasfree-frontend  && \
    cd migasfree-frontend && \
    git checkout $TAG && \
    echo 'MIGASFREE_SERVER=https://__FQDN__' > /migasfree-frontend/.env

RUN cd migasfree-frontend && \
    cp package*.json /app && \
    yarn global add @quasar/cli && \
    yarn && \
    quasar build

FROM nginx:stable-alpine3.20 AS production-stage
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk upgrade --no-cache && \
    apk add curl

# Copy application
COPY --from=build-stage /migasfree-frontend/dist/spa /usr/share/nginx/html
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=5s --timeout=3s CMD /healthcheck.sh || exit 1


COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]

EXPOSE 80

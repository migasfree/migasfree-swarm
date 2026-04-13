FROM node:24-alpine3.22 AS build-stage
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

RUN corepack enable && \
    cd migasfree-frontend && \
    yarn install && \
    yarn dlx @quasar/cli build

FROM nginx:1.29-alpine3.22 AS production-stage
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

RUN apk upgrade --no-cache && \
    apk add curl tzdata musl-locales

# Copy application
COPY --from=build-stage /migasfree-frontend/dist/spa /usr/share/nginx/html
COPY defaults/usr/bin /usr/bin

HEALTHCHECK --start-period=120s --interval=60s --timeout=3s CMD /usr/bin/healthcheck.sh || exit 1


COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]

EXPOSE 80

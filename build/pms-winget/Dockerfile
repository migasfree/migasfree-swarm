ARG TAG=latest
FROM migasfree/core:${TAG} AS core

FROM debian:11.4-slim AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl nano git ca-certificates gnupg wget git git-lfs make cmake clang libicu-dev zlib1g-dev

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

#RUN git clone --branch MSIX-Core-1.2-release --depth 1 https://github.com/microsoft/msix-packaging && \
#    cd /msix-packaging && \
#    ./makelinux.sh --pack --validation-parser -b Release &&  \
#    cp ./.vs/bin/makemsix /usr/bin && \
#    cp ./.vs/lib/libmsix.so /lib/x86_64-linux-gnu && \
#    rm -rf /msix-packaging  && \
#    # Compile other makemsix only for the sign command :-(
#    cd / && \
#    git clone --branch johnmcpms/signing --depth 1 https://github.com/microsoft/msix-packaging && \
#    cd /msix-packaging && \
#    ./makelinux.sh --pack --validation-parser -b Release &&  \
#    cp ./.vs/bin/makemsix /usr/bin/makemsix2 && \
#    cp ./.vs/lib/libmsix.so /lib/x86_64-linux-gnu/libmsix2.so 

RUN git clone --branch johnmcpms/signing --depth 1 https://github.com/mozilla/msix-packaging.git && \
    cd msix-packaging && \
    ./makelinux.sh --pack --validation-parser -b Release &&  \
    cp ./.vs/bin/makemsix /usr/bin/makemsix && \
    cp ./.vs/lib/libmsix.so /lib/x86_64-linux-gnu


FROM debian:11.4-slim
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

COPY VERSION /VERSION

COPY --from=builder /usr/bin/makemsix   /usr/bin/makemsix
COPY --from=builder /lib/x86_64-linux-gnu/libmsix.so   /lib/x86_64-linux-gnu/libmsix.so
#COPY --from=builder /lib/x86_64-linux-gnu/libmsix.so   /lib/x86_64-linux-gnu/libmsix1.so

#COPY --from=builder /usr/bin/makemsix2   /usr/bin/makemsix2
#COPY --from=builder /lib/x86_64-linux-gnu/libmsix2.so   /lib/x86_64-linux-gnu/libmsix2.so

#COPY --from=builder /usr/bin/osslsigncode   /usr/bin/osslsigncode

ENV TAG=${TAG} \
    TERM=xterm \
    DEBIAN_FRONTEND=noninteractive \
    USER=root \
    LANGUAGE=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LANG=C.UTF-8 \
    _UID=890 \
    _GID=890 \
    DJANGO_SETTINGS_MODULE=migasfree.settings.production

RUN _BUILD_DEPENDS=' python3-setuptools python3-pip wget' && \
    _DEPENDS='gnupg dpkg-dev gzip python3  python3-venv netcat-openbsd libicu67 curl apt-utils tzdata' && \
    _PIP_DEPENDS='requests celery[redis] pyyaml importlib-metadata' && \
    usermod -u $_UID www-data && \
    groupmod -g $_GID www-data && \
    chsh -s /bin/bash www-data && \
    apt-get update && \
    apt-get install -y --no-install-recommends  $_DEPENDS && \
    apt-get install -y --no-install-recommends  $_BUILD_DEPENDS && \
    python3 -m venv /venv && \
    . /venv/bin/activate  && \
    pip install --upgrade pip setuptools && \
    pip3 install $_PIP_DEPENDS && \
    mkdir /pms && \
#    chown www-data:www-data /lib/x86_64-linux-gnu/libmsix* && \
    apt-get -y purge $_BUILD_DEPENDS && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 


COPY --from=core /migasfree /pms/migasfree
COPY defaults/usr/bin /usr/bin

COPY defaults/healthcheck.sh /healthcheck.sh
HEALTHCHECK --start-period=2s --interval=10s --timeout=3s CMD /healthcheck.sh || exit 1

RUN chown -R $_UID:$_GID /pms

COPY defaults/docker-entrypoint.sh /docker-entrypoint.sh
COPY defaults/source.template /source.template

ENTRYPOINT ["/bin/bash", "/docker-entrypoint.sh"]

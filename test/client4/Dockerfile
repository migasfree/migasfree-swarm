FROM ubuntu:focal
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt-get install -y --no-install-recommends curl nano git ca-certificates python3-pip python3-netifaces python3-magic python3-distro python3-stdeb python3-pycurl gnupg2 && \
    git clone https://github.com/migasfree/migasfree-client.git && \
    cd /migasfree-client && \
    git checkout  master

RUN cd /migasfree-client && \
    python3 setup.py install

# CA
# ==
COPY defaults/usr/share/ca-certificates/ca.crt /usr/share/ca-certificates/ca.crt

RUN ln -s /usr/share/ca-certificates/ca.crt /usr/local/share/ca-certificates/ca.crt && \
    update-ca-certificates -f

FROM ubuntu:jammy
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt-get install -y --no-install-recommends curl git ca-certificates python3-pip python3-netifaces python3-magic python3-distro python3-stdeb python3-jwcrypto gnupg2 iproute2 pciutils lshw jq nano
    
RUN git clone https://github.com/migasfree/migasfree-client.git && \
    cd /migasfree-client && \
    git checkout REST-API

RUN cd /migasfree-client && \
    pip3 install --no-cache-dir -r requirements.txt && \
    python3 setup.py install

RUN mv /etc/apt/sources.list /etc/apt/sources.list.back

# CA
# ==
COPY defaults/usr/share/ca-certificates/ca.crt /usr/share/ca-certificates/ca.crt

# DEBUG TRAITS
COPY defaults/usr/share/migasfree-client /usr/share/migasfree-client
COPY defaults/usr/local/lib/python3.10/dist-packages/migasfree_client-5.0-beta-py3.10.egg/migasfree_client/sync.py /usr/local/lib/python3.10/dist-packages/migasfree_client-5.0-beta-py3.10.egg/migasfree_client/sync.py


RUN ln -s /usr/share/ca-certificates/ca.crt /usr/local/share/ca-certificates/ca.crt && \
    update-ca-certificates -f

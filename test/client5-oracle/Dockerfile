FROM oraclelinux:8

LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ENV TERM=xterm \
    CURL_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt 
    
RUN yum -y update && \
    yum -y install curl nano git ca-certificates python3-pip python3-netifaces python3-magic python3-distro  python3-jwcrypto gnupg2 procps-ng openssl && \
    git clone https://github.com/migasfree/migasfree-client.git && \
    cd /migasfree-client && \
    git checkout  REST-API 

RUN  cd /migasfree-client && \
    pip3 install  --no-cache-dir  -r  requirements.txt &&\
    python3 setup.py install


# CA
# ==
COPY defaults/usr/share/ca-certificates/ca.crt /etc/pki/ca-trust/source/anchors/ca.crt 

RUN  update-ca-trust extract 

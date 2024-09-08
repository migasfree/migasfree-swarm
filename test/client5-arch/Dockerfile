FROM archlinux:latest
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

RUN patched_glibc=glibc-linux4-2.33-4-x86_64.pkg.tar.zst && \
    curl -LO "https://raw.githubusercontent.com/sickcodes/Docker-OSX/master/${patched_glibc}" && \
    bsdtar -C / -xvf "${patched_glibc}" && \
    pacman -Sy && \
    pacman --noconfirm --sync curl nano git ca-certificates python-pip python-netifaces python-magic python-distro python-jwcrypto gnupg && \
    git clone https://github.com/migasfree/migasfree-client.git && \
    cd /migasfree-client && \
    git checkout  REST-API

RUN  cd /migasfree-client && \
    pip3 install --no-cache-dir -r requirements.txt && \
    python setup.py install

# CA
# ==
COPY defaults/usr/share/ca-certificates/ca.crt /etc/ca-certificates/trust-source/anchors/ca.crt

RUN trust extract-compat

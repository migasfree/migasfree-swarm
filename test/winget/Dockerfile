#FROM ubuntu:focal
FROM gcc:11.2.0
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ENV TERM=xterm \
    DEBIAN_FRONTEND=noninteractive 
    
RUN apt update && \
    apt-get install -y --no-install-recommends curl nano git ca-certificates gnupg2 wget git


#RUN apt update && \
#    apt-get install -y --no-install-recommends curl nano git ca-certificates python3-pip gnupg2 wget osslsigncode git

#RUN  pip3 install  --no-cache-dir  winsign aiohttp


#RUN git clone https://github.com/mozilla-releng/winsign.git
#RUN cd winsign && \
#    git checkout tags/2.1.0 && \
#   python3 setup.py install 





#RUN wget https://raw.githubusercontent.com/catlee/winsign/master/tests/data/cert.pem
#RUN wget https://raw.githubusercontent.com/catlee/winsign/master/tests/data/privkey.pem



RUN git clone https://github.com/microsoft/msix-packaging  && \
    cd msix-packaging && \
    git checkout johnmcpms/signing


RUN apt -y  install cmake clang  

RUN mkdir /usr/include/machine && \
    cp  /usr/include/endian.h /usr/include/machine/endian.h

RUN  cd msix-packaging && \
    ./makelinux.sh --pack --validation-parser -b Release &&  \
    cp ./.vs/bin/makemsix /usr/bin


# compile command makemsix is required
# make cmake clang libicu-dev libssl-dev zlib1g zlib1g-dev zlibc libgzstream-dev libghc-pipes-zlib-dev libghc-zlib-bindings-dev libghc-openssl-streams-dev libghc-cryptohash-sha256-dev libskstream-0.3-dev && \
#RUN apt -y  install make cmake clang libicu-dev libssl-dev llvm llvm-dev    libclang-9-dev && \

#RUN apt -y  install cmake clang   libicu-dev libssl-dev  lib64gcc-s1 && \   
#    cd msix-packaging && \
#    git checkout johnmcpms/signing && \
#    ./makelinux.sh --pack --validation-parser -b Release &&  \
#    cp ./.vs/bin/makemsix /usr/bin


# CA
# ==
COPY defaults/usr/share/ca-certificates/ca.crt /usr/share/ca-certificates/ca.crt

RUN ln -s /usr/share/ca-certificates/ca.crt /usr/local/share/ca-certificates/ca.crt && \
    update-ca-certificates -f

#RUN wget https://winget.azureedge.net/cache/source.msix 
COPY source /source



# Crear fichero pfx para firmar msix
# ===========================
# 1.- creamos cert.pfx a partir del certificado y clave privada
# 2.- Empaquetamos el directirio en un fichero msix
# 3.- Firmamos el .msix (se añade AppxSignature.ptx)
# 4.- Lo ponemos en el repo

#openssl pkcs12 -export -in /certificates/cert.crt  -inkey /certificates/cert.key -out cert.pfx -certfile  /certificates/ca.crt -passin pass:"" -passout pass:"" -descert
#makemsix pack -d source -p source.msix
#makemsix sign -p source.msix -c cert.pfx -cf PFX
#cp source.msix /public/winget-pkgs-master/




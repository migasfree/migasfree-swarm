FROM minio/minio:latest
LABEL maintainer="Alberto Gacías <alberto@migasfree.org>"

ARG TAG=latest

ENV TAG=${TAG}

COPY VERSION /VERSION

VOLUME ["/data"]

CMD ["minio"]

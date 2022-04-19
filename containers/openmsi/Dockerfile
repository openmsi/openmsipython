# Alpine 3.13 needed for CentOS 7.x host compatibility; remove version number for most other podman/docker hosts
FROM python:3.9-alpine3.13

USER root

#labels
LABEL Build docker build --rm --tag paradim/openmsi .

#start in the default area
WORKDIR /

# build known-good librdkafka
RUN apk add bash curl gcc g++ make musl-dev bsd-compat-headers perl && \
    curl -L https://github.com/edenhill/librdkafka/archive/v1.8.2.tar.gz > ./v1.8.2.tar.gz && \
    tar -zxvf v1.8.2.tar.gz && \
    cd /librdkafka-1.8.2 && \
    ./configure --install-deps --disable-gssapi --disable-lz4-ext --enable-static $* && \
    make -j && \
    examples/rdkafka_example -X builtin.features && \
    CI=true make -C tests run_local_quick && \
    make install && \
    apk del curl perl g++ gcc make musl-dev bsd-compat-headers && \
    cd / && \
    rm -rf /librdkafka-1.8.2

#install binary bits for use with pip install later
RUN apk update && \
    apk add binutils libsodium libsodium-dev musl musl-dev openblas openblas-dev libpng libpng-dev bzip2 bzip2-dev zlib zlib-dev freetds freetds-dev gfortran gcc g++ make git

#clone the openmsipython repo and install it
RUN git clone https://github.com/openmsi/openmsipython.git
WORKDIR /openmsipython
RUN pip install .

# remove unneeded building bits (libsodium-dev required to stay)
RUN apk del gfortran gcc g++ git make openblas-dev libpng-dev bzip2-dev zlib-dev freetds-dev musl-dev

#switch back to the default area
WORKDIR /

# Need to add specific OpenMSIPython entrypoint


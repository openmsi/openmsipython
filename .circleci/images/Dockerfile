# CircleCI image from https://hub.docker.com/r/cimg/python
FROM cimg/python:3.9

# Switch to root user
USER root

# Install miniconda3
ENV PATH="/root/miniconda3/bin:$PATH"
ARG PATH="/root/miniconda3/bin:$PATH"
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 

# Install libsodium
RUN conda install -c anaconda libsodium

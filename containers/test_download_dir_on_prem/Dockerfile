# CircleCI image from https://hub.docker.com/r/cimg/python
FROM cimg/python:3.9

#switch to root user
USER root

#make the output directory
RUN mkdir /output_dir

#labels
ENV RUNDIR="/home/neminiz1/dmref"
LABEL Build docker build --rm --tag openmsi/test_download_dir_on_prem .
LABEL Run docker run --rm -it \
      --mount type=bind,source=${RUNDIR}/kafka_downloads/test_download_dir,target=/output_dir \
      --mount type=bind,source=${RUNDIR}/more_config_files,target=/config \
      openmsi/test_download_dir_on_prem

#start in the default area
WORKDIR /

#install miniconda 3
ENV PATH="/root/miniconda3/bin:$PATH"
ARG PATH="/root/miniconda3/bin:$PATH"
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 

#install libsodium
RUN conda install -c anaconda libsodium

#install git
RUN conda install -c anaconda git

#clone the openmsipython repo and install it
RUN git clone https://github.com/openmsi/openmsipython.git
WORKDIR /openmsipython
RUN git checkout on_prem_broker
RUN pip install .

#switch back to the default area
WORKDIR /

#Run DataFileDownloadDirectory
ENTRYPOINT [ "DataFileDownloadDirectory", "/output_dir", \
             "--config", "/config/test_on_prem.config", \
             "--topic_name", "testing", \
             "--consumer_group_ID", "testing_1", \
             "--n_threads", "1" \
        ]
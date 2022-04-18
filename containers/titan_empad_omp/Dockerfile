FROM cimg/python:3.9

USER root

#make the output directory
RUN mkdir /output_dir

#labels
LABEL Build docker build --rm --tag openmsi/titan_empad_omp .
LABEL Run docker run --rm -it \
      --mount type=bind,source=/path/to/jbod/output/dir,target=/output_dir \
      --mount type=bind,source=/home/neminiz1/dmref/more_config_files,target=/config \
      openmsi/titan_empad_omp

#start in the default area
WORKDIR /

#install libsodium
RUN apt-get update -y && \
    apt-get install -y libsodium-dev

#install git
RUN apt-get install -y git

#clone the openmsipython repo and install it
RUN git clone https://github.com/openmsi/openmsipython.git
WORKDIR /openmsipython
RUN pip install .

#switch back to the default area
WORKDIR /

#Run DataFileDownloadDirectory
ENTRYPOINT [ "DataFileDownloadDirectory", "/output_dir", \
             "--config", "/config/titan_empad_omp.config", \
             "--topic_name", "titan-empad-omp", \
             "--consumer_group_ID", "titan-empad-omp-consumer-v1", \
             "--n_threads", "1" \
        ]

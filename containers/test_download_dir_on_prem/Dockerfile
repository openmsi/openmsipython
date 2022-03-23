FROM cimg/python:3.9

USER root

#make the output directory
RUN mkdir /output_dir

#labels
LABEL Build docker build --rm --tag openmsi/test_download_dir_on_prem .
LABEL Run docker run --rm -it \
      --mount type=bind,source=/home/neminiz1/dmref/kafka_downloads/test_download_dir,target=/output_dir \
      --mount type=bind,source=/home/neminiz1/dmref/more_config_files,target=/config \
      openmsi/test_download_dir_on_prem

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
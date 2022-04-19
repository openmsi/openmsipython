FROM paradim/openmsi

#make the output directory
RUN mkdir /output_dir

#labels
LABEL Build docker build --rm --tag paradim/openmsi-titan-empad .
LABEL Run docker run --rm -it \
      --mount type=bind,source=/path/to/jbod/output/dir,target=/output_dir \
      --mount type=bind,source=/home/neminiz1/dmref/more_config_files,target=/config \
      paradim/openmsi-titan-empad

#switch back to the default area
WORKDIR /

#Run DataFileDownloadDirectory
ENTRYPOINT [ "DataFileDownloadDirectory", "/output_dir", \
             "--config", "/config/titan_empad_omp.config", \
             "--topic_name", "titan-empad-omp", \
             "--consumer_group_ID", "titan-empad-omp-consumer-v1", \
             "--n_threads", "1" \
           ]

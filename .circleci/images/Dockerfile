# CircleCI image from https://hub.docker.com/r/cimg/python
FROM cimg/python:3.9

# Switch to root user
USER root

# Install systemd
RUN sudo apt-get upgrade
RUN sudo apt-get install systemd
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done);
RUN rm -f /lib/systemd/system/multi-user.target.wants/*;
RUN rm -f /etc/systemd/system/*.wants/*;
RUN rm -f /lib/systemd/system/local-fs.target.wants/*;
RUN rm -f /lib/systemd/system/sockets.target.wants/*udev*;
RUN rm -f /lib/systemd/system/sockets.target.wants/*initctl*;
RUN rm -f /lib/systemd/system/basic.target.wants/*;
RUN rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]

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

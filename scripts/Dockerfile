FROM ubuntu:18.04

RUN apt-get update;apt-get install -y python3.6 curl git locales language-pack-en
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN git clone https://github.com/threefoldtech/jumpscaleX.git

RUN python3.6 jumpscaleX/install/install.py -1 -y -w -p

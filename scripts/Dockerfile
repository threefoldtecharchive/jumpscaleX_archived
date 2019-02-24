FROM ubuntu:18.04

ARG commit
RUN apt-get update;apt-get install -y python3.6 curl git locales language-pack-en
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN mkdir -p /sandbox/code/github/threefoldtech
RUN cd /sandbox/code/github/threefoldtech; git clone https://github.com/threefoldtech/jumpscaleX.git
RUN cd /sandbox/code/github/threefoldtech/jumpscaleX; git reset --hard $commit

RUN python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -1 -y 

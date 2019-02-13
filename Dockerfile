FROM ubuntu:18.04

ADD . /sandbox/code/github/threefoldtech/jumpscaleX

RUN apt-get update;apt-get install -y python3.6 curl git locales language-pack-en
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -1 -y -w 

RUN pip3 install pytest pytest-cov codecov
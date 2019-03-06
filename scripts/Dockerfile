FROM ubuntu:18.04

ARG branch
ARG commit
RUN apt-get update;apt-get install -y python3.6 curl git locales language-pack-en python3-nose
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
RUN mkdir -p /sandbox/code/github/threefoldtech
RUN cd /sandbox/code/github/threefoldtech; git clone --branch https://github.com/threefoldtech/jumpscaleX.git
RUN cd /sandbox/code/github/threefoldtech/jumpscaleX/; git reset --hard $commit

RUN python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -1 -y -w -p
RUN /bin/bash -c "source /sandbox/env.sh; js_shell 'j.builder.db.zdb.install()'"
RUN cd /sandbox/code/github/threefoldtech/jumpscaleX/; git checkout Jumpscale/jumpscale_generated.py docs/errors.md
RUN pip3 install pytest

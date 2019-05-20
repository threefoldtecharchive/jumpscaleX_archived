FROM ubuntu:18.04

ADD . /sandbox/code/github/threefoldtech/jumpscaleX

ENV INSYSTEM=1
ENV USEGIT=1

RUN apt-get update;apt-get install -y python3.6 curl git locales
RUN python3.6 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py $INSYSTEM y

RUN pip3 install pytest pytest-cov pytest-testconfig codecov
RUN echo '[[instruction]] \ninstruction_method = "j.data.nacl.configure" \nname = "default" \nsecret = "123" \ngenerate = true \nsshagent_use = false' > /sandbox/nacl_config.toml

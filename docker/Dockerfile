FROM ubuntu:16.04

ENV MZN 2.1.6
ENV MZN_BASENAME MiniZincIDE-${MZN}-bundle-linux-x86_64
ENV MZN_GH_BASE https://github.com/MiniZinc/MiniZincIDE
ENV MZN_DL_URL ${MZN_GH_BASE}/releases/download/${MZN}/${MZN_BASENAME}.tgz

RUN apt-get update -y \
    && apt-get install -y vim wget libmpfr-dev \
    && apt-get install -y git libqt5printsupport5 build-essential \
    && apt-get install -y python3 python3-setuptools python3-dev \
    && easy_install3 pip \
    && pip install --upgrade virtualenv pip wheel 

# Minizinc
RUN wget -q $MZN_DL_URL -O mz.tgz \
    && tar xzf mz.tgz \
    && mv $MZN_BASENAME /mz-dist \
    && rm mz.tgz \
    && echo PATH=/mz-dist:$PATH >> ~/.bashrc

ENV SHELL /bin/bash
ENV PATH /mz-dist:$PATH

# OSDF
RUN git clone http://gerrit.onap.org/r/optf/osdf \
    && pip install --no-cache-dir -r osdf/requirements.txt

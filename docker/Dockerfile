#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

FROM ubuntu:16.04

ENV OSDF_PORT "8699"
EXPOSE ${OSDF_PORT}

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

RUN ln -s /usr/bin/python3.5 /usr/bin/python

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
    && git checkout beijing \
    && pip install --no-cache-dir -r osdf/requirements.txt

CMD [ "/osdf/osdfapp.sh" ]

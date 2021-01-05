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

FROM ubuntu:20.04

ARG MVN_ARTIFACT_VERSION
ARG REPO
ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
ARG DEBIAN_FRONTEND=noninteractive

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY

ENV OSDF_PORT "8699"
EXPOSE ${OSDF_PORT}

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends software-properties-common wget \
    curl ca-certificates vim unzip zip git binutils binfmt-support build-essential  \
    python3 python3-setuptools python3-dev \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && curl -s https://bootstrap.pypa.io/get-pip.py | python \
    && python -m pip --no-cache-dir  install --upgrade pip wheel setuptools && rm -rf /var/lib/apt/lists/*

ARG MZN_DL_URL=https://github.com/MiniZinc/MiniZincIDE/releases/download/2.4.3/MiniZincIDE-2.4.3-bundle-linux-x86_64.tgz

# Minizinc
RUN wget -q $MZN_DL_URL -O /tmp/mz.tgz \
    && mkdir -p /mz-dist && tar xzf /tmp/mz.tgz -C /mz-dist --strip-components 1\
    && rm /tmp/mz.tgz

ENV SHELL /bin/bash
ENV PATH /mz-dist/bin:$PATH

# OSDF
WORKDIR /opt/osdf
#RUN wget -O /opt/osdf.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=releases&g=org.onap.optf.osdf&a=optf-osdf&e=zip&v=1.3.4" && \
#    unzip -q -o -B /opt/osdf.zip -d /opt/ && \
#    rm -f /opt/osdf.zip
RUN groupadd onap \
    && useradd -m -g onap onap

COPY onap-osdf-tm/optf-osdf-${MVN_ARTIFACT_VERSION}.zip /tmp/optf-osdf.zip
COPY onap-osdf-tm/apps /opt/osdf/apps
RUN unzip -q -o -B /tmp/optf-osdf.zip -d /opt/ && rm -f /tmp/optf-osdf.zip

RUN mkdir -p /var/log/onap/optf/osdf/ \
    && chown -R onap:onap /var/log/onap \
    && chown -R onap:onap /opt/osdf

RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-osdf.txt

USER onap

CMD [ "/opt/osdf/osdfapp.sh", "-x", "osdfapp.py" ]

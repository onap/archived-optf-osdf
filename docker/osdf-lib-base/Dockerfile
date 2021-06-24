#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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

FROM python:3.9-slim-buster

ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}
ARG DEBIAN_FRONTEND=noninteractive

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY

RUN groupadd onap \
    && useradd -m -g onap onap

# Minizinc
RUN apt-get update \
    && apt-get install -y wget \
    && wget -q https://github.com/MiniZinc/MiniZincIDE/releases/download/2.4.3/MiniZincIDE-2.4.3-bundle-linux-x86_64.tgz -O /tmp/mz.tgz \
    && mkdir -p /mz-dist && tar xzf /tmp/mz.tgz -C /mz-dist --strip-components 1\
    && rm /tmp/mz.tgz \
    && wget -q https://github.com/google/or-tools/releases/download/v7.8/or-tools_ubuntu-20.04_v7.8.7959.tar.gz -O /tmp/flatzinc.tar.gz \
    && mkdir -p /ortools \
    && tar zxf /tmp/flatzinc.tar.gz -C /ortools --strip-components 1 \
    && rm /tmp/flatzinc.tar.gz \
    && apt-get remove -y wget

ENV SHELL /bin/bash
ENV PATH /mz-dist/bin:$PATH

COPY onap-osdf-tm/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

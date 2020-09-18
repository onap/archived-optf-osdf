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

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends software-properties-common \
    curl ca-certificates vim binutils binfmt-support build-essential  \
    python3 python3-setuptools python3-dev \
    && ln -s /usr/bin/python3.8 /usr/bin/python \
    && curl -s https://bootstrap.pypa.io/get-pip.py | python \
    && python -m pip --no-cache-dir  install --upgrade pip wheel setuptools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY sim /sim
COPY start_sim.sh /start_sim.sh

CMD ["/start_sim.sh"]
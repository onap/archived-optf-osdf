#
# -------------------------------------------------------------------------
#   Copyright (c) 2020 AT&T Intellectual Property
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

FROM python:3.8-alpine

ARG MVN_ARTIFACT_VERSION
ARG REPO
ARG HTTP_PROXY=${HTTP_PROXY}
ARG HTTPS_PROXY=${HTTPS_PROXY}

ENV http_proxy $HTTP_PROXY
ENV https_proxy $HTTPS_PROXY

ENV OSDF_PORT "8699"
EXPOSE ${OSDF_PORT}

ENV MZN 2.4.2
ENV MZN_BASENAME MiniZincIDE-${MZN}-bundle-linux
ENV MZN_GH_BASE https://github.com/MiniZinc/MiniZincIDE
ENV MZN_DL_URL ${MZN_GH_BASE}/releases/download/${MZN}/${MZN_BASENAME}-x86_64.tgz

RUN apk update  && apk upgrade \
    && apk --no-cache --update add --virtual build-deps openssl wget  \
    && apk --no-cache --update add less ca-certificates bash libxslt-dev unzip \
                                freetype freetype-dev libstdc++ build-base libc6-compat lapack-dev openblas-dev \
    && ln -s /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2 \
    && pip install --no-cache-dir --upgrade pip wheel setuptools

# Minizinc
RUN wget -q $MZN_DL_URL -O mz.tgz \
    && tar xzf mz.tgz \
    && mv $MZN_BASENAME /mz-dist \
    && rm mz.tgz \
    && echo PATH=/mz-dist/bin:$PATH >> ~/.bashrc

ENV SHELL /bin/bash
ENV PATH /mz-dist/bin:$PATH

RUN addgroup -S onap && adduser -S -G onap onap

# OSDF
WORKDIR /opt/osdf
#RUN wget -O /opt/osdf.zip "https://nexus.onap.org/service/local/artifact/maven/redirect?r=releases&g=org.onap.optf.osdf&a=optf-osdf&e=zip&v=1.3.4" && \
#    unzip -q -o -B /opt/osdf.zip -d /opt/ && \
#    rm -f /opt/osdf.zip

COPY onap-osdf-tm/optf-osdf-${MVN_ARTIFACT_VERSION}.zip /tmp/optf-osdf.zip
COPY onap-osdf-tm/runtime /opt/osdf/runtime
COPY onap-osdf-tm/requirements-opteng.txt .
RUN unzip -q -o -B /tmp/optf-osdf.zip -d /opt/ && rm -f /tmp/optf-osdf.zip
RUN mkdir -p /var/log/onap/optf/osdf/ \
    && chown onap:onap /var/log/onap -R \
    && chown onap:onap /opt/osdf -R

RUN pip install --no-cache-dir -r requirements.txt -r requirements-opteng.txt\
    && apk del build-deps && rm -rf /var/cache/apk/*

USER onap

CMD [ "/opt/osdf/osdfapp.sh", "-x", "solverapp.py", "-c", "/opt/osdf/config/opteng_config.yaml" ]

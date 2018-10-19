#!/bin/bash

# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

cd $(dirname $0)

# bash ../etc/make-certs.sh  # create the https certificates if they are not present

LOGS=logs
mkdir -p $LOGS

export OSDF_CONFIG_FILE=${1:-/opt/app/config/osdf_config.yaml}  # this file may be passed by invoker
[ ! -e "$OSDF_CONFIG_FILE" ] && unset OSDF_CONFIG_FILE

if [ -e /opt/app/ssl_cert/aaf_root_ca.cer ]; then
    #assuming that this would be an ubuntu vm.
    cp /opt/app/ssl_cert/aaf_root_ca.cer /usr/local/share/ca-certificates/aafcacert.crt
    chmod 444 /usr/local/share/ca-certificates/aafcacert.crt
    update-ca-certificates
fi

if [ -e /etc/ssl/certs/aafcacert.pem ]; then
    export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
else
    export REQUESTS_CA_BUNDLE=/opt/app/ssl_cert/aaf_root_ca.cer
fi

python osdfapp.py 2>$LOGS/err.log 1>$LOGS/out.log < /dev/null  # running the app 

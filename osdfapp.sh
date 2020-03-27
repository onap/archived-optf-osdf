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

usage() {
	echo "Usage:"
	echo "    $0 -h Display this help message."
	echo "    $0 -c configfile_path(optional) -x app.py file"
	exit 0
}

cd $(dirname $0)

# bash ../etc/make-certs.sh  # create the https certificates if they are not present

while getopts ":hc:x:" opt; do
  case ${opt} in
    h )
      usage
      ;;
    c )
      # process option configuration
      export OSDF_CONFIG_FILE=$OPTARG
      ;;
    x )
      # process executable file
      export EXEC_FILE=$OPTARG
      ;;
    ? )
      usage
      ;;
    : )
      echo "Invalid Option: -$OPTARG requires an argument" 1>&2
      exit 1
     ;;
  esac
done
shift $(( OPTIND - 1 ))

set -e

LOGS=logs
mkdir -p $LOGS

#if [ -e /opt/app/ssl_cert/aaf_root_ca.cer ]; then
#    #assuming that this would be an ubuntu vm.
#    cp /opt/app/ssl_cert/aaf_root_ca.cer /usr/local/share/ca-certificates/aafcacert.crt
#    chmod 444 /usr/local/share/ca-certificates/aafcacert.crt
#    update-ca-certificates
#fi

export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

if [ ! -z "$EXEC_FILE" ]
then
	# flask run
	echo "Running $EXEC_FILE"
	python $EXEC_FILE # running the app
else
    usage
fi

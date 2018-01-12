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

# Call osdf app after setting LD_LIBRARY_PATH for oracle client, postgres client, etc.

cd $(dirname $0)

# Environment variables below are for ORACLE_HOME and such things, and not needed for 1707 onwards
# . ../dependencies/env.sh

bash ../etc/make-certs.sh  # create the https certificates if they are not present

set -e

mkdir -p logs

if [ ! -e "osdf-optim" ]; then
(
  mkdir tmp
  cd tmp
  tar xzf ../../dependencies/SNIROOptimizationPack.tgz
  mv osdf ../osdf-optim
  cd ../osdf-optim/pywheels
  pip install docopt* jsonschema*
)
cp etc/run-case-local.sh osdf-optim/run/
fi

if [ $# -ge 1 ]; then
   export SNIRO_MANAGER_CONFIG_FILE="$1"  # this file is passed by the DCAE controller
fi

# export FLASK_APP=osdfapp.py

# flask run
python osdfapp.py # running the app 

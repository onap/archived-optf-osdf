#!/bin/bash
#
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

# This script is in osdf/test/functest/scripts/

SCRIPTDIR=$(dirname $(readlink -f $0))
FUNC_TEST_DIR=$(dirname $SCRIPTDIR)
TEST_DIR=$(dirname $FUNC_TEST_DIR)
OSDF_DIR=$(dirname $TEST_DIR)
SIMULATORS_DIR=$FUNC_TEST_DIR/simulators

# Copy policy files from $TEST_DIR/policy-local-files into $SIMULATORS_DIR/policy/response-payloads
(
    cd $SIMULATORS_DIR
    cp $TEST_DIR/policy-local-files/*.json $SIMULATORS_DIR/policy/response-payloads/pdp-has-vcpe-good
)


# start the flask application after linking the code location and config folder
(
    cd $SIMULATORS_DIR
    ln -s $OSDF_DIR/osdf .
    ln -s $SIMULATORS_DIR/simulated-config config

    XPID=$(ps -x | grep "python oof_dependencies_simulators.py" | grep -v grep | awk '{print $1}')
    if [ -z "$XPID" ]; then
      python oof_dependencies_simulators.py > simulator-logs 2>&1 &
      sleep 5
    fi
) 




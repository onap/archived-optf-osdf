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

# We don't need all the directory names here and the "cd", but it may be needed later on
# Also, it will be a guard against some bad config where the directory doesn't exist

if [[ `uname` == "Darwin" ]]
then
  SCRIPTDIR=$(dirname $(greadlink -f $0))
else
  SCRIPTDIR=$(dirname $(readlink -f $0))
fi
FUNC_TEST_DIR=$(dirname $SCRIPTDIR)
TEST_DIR=$(dirname $FUNC_TEST_DIR)
OSDF_DIR=$(dirname $TEST_DIR)
SIMULATORS_DIR=$FUNC_TEST_DIR/simulators

cd $SIMULATORS_DIR

XPID=$(ps -x | grep "python oof_dependencies_simulators.py" | grep -v grep | awk '{print $1}')
if [ -n "$XPID" ]; then
  kill $XPID
fi

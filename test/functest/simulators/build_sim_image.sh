#!/bin/bash
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

if [[ `uname` == "Darwin" ]]
then
  SCRIPTDIR=$(dirname $(greadlink -f $0))
else
  SCRIPTDIR=$(dirname $(readlink -f $0))
fi

FUNC_TEST_DIR=$(dirname $SCRIPTDIR)
TEST_DIR=$(dirname $FUNC_TEST_DIR)
SIMULATORS_DIR=$FUNC_TEST_DIR/simulators
OSDF_DIR=$(dirname $TEST_DIR)
DOCKER_DIR=$SIMULATORS_DIR/tmp_docker

echo "Before Docker Build"
cat $OSDF_DIR/requirements.txt
echo $OSDF_DIR

exit 0
mkdir -p $DOCKER_DIR/sim/osdf/policy/response-payloads/pdp-has-vcpe-good

cp $SIMULATORS_DIR/Dockerfile $DOCKER_DIR/.

cp -r $OSDF_DIR/osdf $DOCKER_DIR/sim
mkdir -p $DOCKER_DIR/sim/config/
cp $SIMULATORS_DIR/simulated-config/*.yaml $DOCKER_DIR/sim/config/
cp $SIMULATORS_DIR/simulated-config/*.yml $DOCKER_DIR/sim/config/
cp $SIMULATORS_DIR/simulated-config/*.config $DOCKER_DIR/sim/config/
cp -r $SIMULATORS_DIR/configdb $DOCKER_DIR/sim
cp -r $SIMULATORS_DIR/has-api $DOCKER_DIR/sim
cp -r $SIMULATORS_DIR/policy $DOCKER_DIR/sim
cp -r $SIMULATORS_DIR/aai $DOCKER_DIR/sim
cp $TEST_DIR/policy-local-files/*.json $DOCKER_DIR/sim/policy/response-payloads/pdp-has-vcpe-good
cp $TEST_DIR/placement-tests/policy_response.json $DOCKER_DIR/sim/policy/response-payloads/
cp $SIMULATORS_DIR/oof_dependencies_simulators.py $DOCKER_DIR/sim/oof_dependencies_simulators.py
cp $OSDF_DIR/requirements.txt $DOCKER_DIR
cp -r $SIMULATORS_DIR/start_sim.sh $DOCKER_DIR/

cd $DOCKER_DIR

docker build -t osdf_sim .

rm -rf $DOCKER_DIR

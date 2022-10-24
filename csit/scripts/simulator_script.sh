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

echo "### This is ${WORKSPACE}/scripts/simulator_script.sh"
#
# add here whatever commands is needed to prepare the optf/osdf CSIT testing
#

#echo "i am ${USER} : only non jenkins users may need proxy settings"
if [ ${USER} != 'jenkins' ]; then

    # add proxy settings into this script when you work behind a proxy
    ${WORKSPACE}/scripts/osdf_proxy_settings.sh ${WORK_DIR}

fi

# prepare osdf_sim
cd ${WORKSPACE}/../test/functest/simulators

# check Dockerfile content
cat ./Dockerfile

# build osdf_sim
chmod +x ./build_sim_image.sh
./build_sim_image.sh

# run osdf_sim
docker run -d --name osdf_sim -p "5000:5000"  osdf_sim:latest;

docker ps -a

OSDF_SIM_IP=`${WORKSPACE}/scripts/get-instance-ip.sh osdf_sim`
echo "OSDF_SIM_IP=${OSDF_SIM_IP}"

docker inspect osdf_sim

${WORKSPACE}/scripts/wait_for_port.sh ${OSDF_SIM_IP} 5000


# wait a while before continuing
sleep 2

echo "inspect docker things for tracing purpose"


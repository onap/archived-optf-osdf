# -------------------------------------------------------------------------
#   Copyright (c) 2020 Huawei Intellectual Property
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

import json
import os
BASE_DIR = os.path.dirname(__file__)
"""
This application generates NST SELECTION API calls using the information received from SO
"""

def buildSolution(request_json):
    return {
        "NSTsolution" : getNSTSolution(request_json)
    }

def getNSTSolution(request_json):
# the file is in the same folder for now will move it to the conf folder of the has once its integrated there...
    config_input_json = os.path.join(BASE_DIR, 'conf/configIinputs.json')
    try:
        with open(config_input_json, 'r') as openfile:
            serviceProfile = request_json["serviceProfile"]
            resourceName = "NST"
            serviceProfileParameters = serviceProfile["serviceProfileParameters"]
            nst_object = json.load(openfile)
            foundNst = False
            for nst in nst_object[resourceName]:
                [(nstName, nstList)] = nst.items()
                matchall = False
                for constraint_name in serviceProfileParameters:
                    value = serviceProfileParameters[constraint_name]
                    constraint_value= nstList[constraint_name]
                    if constraint_value != value:
                        matchall = False
                        break
                    else:
                        matchall = True
                if matchall:
                    foundNst = True
                    NSTName = nstList["name"]
                    matchlevel = 1
        if not(foundNst):
            NSTName = None
            matchlevel = 0
        return {
            "invariantUUID" : "INvariant UUID",
            "UUID" : "uuid",
            "NSTName" : NSTName,
            "matchLevel" : matchlevel
        }
    except Exception as err:
        raise err


def process_nst_selection( request_json, osdf_config):
    """
    Process a PCI request from a Client (build config-db, policy and  API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :return: response from NST Opt
    """
    solution = buildSolution(request_json)

    return {
        "requestId" : request_json['requestInfo']['requestId'],
        "transactionId" : request_json['requestInfo']['transactionId'],
        "statusMessage" : " ",
        "requestStatus" : "accepted",
        "solutions" : solution
    }
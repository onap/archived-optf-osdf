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

"""
This application generates NST SELECTION API calls using the information received from SO
"""
import json
import os
import traceback
from requests import RequestException
from osdf.logging.osdf_logging import error_log
from osdf.utils.interfaces import get_rest_client
from threading import Thread
BASE_DIR = os.path.dirname(__file__)


class NstSelection(Thread):
    def __init__(self, osdf_config, request_json, model_type):
        super().__init__()
        self.osdf_config = osdf_config
        self.request_json = request_json
        self.model_type = model_type

    def run(self):
        self.process_nst_selection()

    def process_nst_selection(self):

        """
        Process a PCI request from a Client (build config-db, policy and  API call, make the call, return result)
        :param req_object: Request parameters from the client
        :param osdf_config: Configuration specific to OSDF application (core + deployment)
        :return: response from NST Opt
        """
        req_info = self.request_json['requestInfo']
        rc = get_rest_client(self.request_json, service='so')
        solution = self.get_nst_solution()
        try:
            rc.request(json=solution, noresponse=True)
        except RequestException:
            error_log.error("Error sending asynchronous notification for {} {}".format(req_info['requestId'],
                                                                                       traceback.format_exc()))

    def get_nst_solution(self):
        # the file is in the same folder for now will move it to the conf folder of the has once its
        # integrated there...
        config_input_json = os.path.join(BASE_DIR, 'conf/configIinputs.json')
        try:
            with open(config_input_json, 'r') as openfile:
                serviceProfile = self.request_json["serviceProfile"]
                nstSolutionList = []
                resourceName = "NST"
                serviceProfileParameters = serviceProfile["serviceProfileParameters"]
                nst_object = json.load(openfile)
                for nst in nst_object[resourceName]:
                    [(nstName, nstList)] = nst.items()
                    individual_nst = dict()
                    matchall = False
                    for constraint_name in serviceProfileParameters:
                        value = serviceProfileParameters[constraint_name]
                        constraint_value = nstList.get(constraint_name)
                        if (not constraint_value):
                            matchall = False
                            break
                        else:
                            matchall = True
                    if matchall:
                        individual_nst["NSTName"] = nstList.get("name")
                        individual_nst["UUID"] = nstList.get("modeluuid")
                        individual_nst["invariantUUID"] = nstList.get("modelinvariantuuid")
                        individual_nst["individual_nst"] = 1
                        nstSolutionList.append(individual_nst)

            return nstSolutionList
        except Exception as err:
            raise err

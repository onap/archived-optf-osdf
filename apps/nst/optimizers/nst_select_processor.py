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
from osdf.logging.osdf_logging import error_log
from osdf.utils.interfaces import get_rest_client
from requests import RequestException
from threading import Thread
import traceback
BASE_DIR = os.path.dirname(__file__)


# This is the class for NST Selection


class NstSelection(Thread):

    def __init__(self, osdf_config, request_json):
        super().__init__()
        self.osdf_config = osdf_config
        self.request_json = request_json
        self.request_info = self.request_json['requestInfo']

    def run(self):
        self.process_nst_selection()

    def process_nst_selection(self):
        """Process a PCI request from a Client (build config-db, policy and  API call, make the call, return result)

            :param req_object: Request parameters from the client
            :param osdf_config: Configuration specific to OSDF application (core + deployment)
            :return: response from NST Opt
        """
        try:
            rest_client = get_rest_client(self.request_json, service='so')
            solution = self.get_nst_solution()
            solution = self.get_nst_selection_response(solution)
        except Exception as err:
            error_log.error("Error for {} {}".format(self.request_info.get('requestId'),
                                                     traceback.format_exc()))
            error_message = str(err)
            solution = self.error_response(error_message)

        try:
            rest_client.request(json=solution, noresponse=True)
        except RequestException:
            error_log.error("Error sending asynchronous notification for {} {}".
                            format(self.request_info['requestId'], traceback.format_exc()))

    def get_nst_solution(self):
        """the file is in the same folder for now will move it to the conf folder of the has once its

           integrated there...
        """

        config_input_json = os.path.join(BASE_DIR, 'conf/configIinputs.json')
        with open(config_input_json, 'r') as openfile:
            service_profile = self.request_json["serviceProfile"]
            nst_solution_list = []
            resource_name = "NST"
            nst_object = json.load(openfile)
            for nst in nst_object[resource_name]:
                [(nst_name, nst_list)] = nst.items()
                individual_nst = dict()
                matchall = False
                for constraint_name in service_profile:
                    constraint_value = nst_list.get(constraint_name)
                    if not constraint_value:
                        matchall = False
                        break
                    else:
                        matchall = True
                if matchall:
                    individual_nst["NSTName"] = nst_list.get("name")
                    individual_nst["UUID"] = nst_list.get("modeluuid")
                    individual_nst["invariantUUID"] = nst_list.get("modelinvariantuuid")
                    individual_nst["individual_nst"] = 1
                    nst_solution_list.append(individual_nst)

        return nst_solution_list

    def get_nst_selection_response(self, solutions):
        """Get NST selection response from final solution

            :param solutions: final solutions
            :return: NST selection response to send back as dictionary
        """
        return {'requestId': self.request_info['requestId'],
                'transactionId': self.request_info['transactionId'],
                'requestStatus': 'completed',
                'statusMessage': '',
                'solutions': solutions}

    def error_response(self, error_message):
        """Form response message from the error message

            :param error_message: error message while processing the request
            :return: response json as dictionary
        """
        return {'requestId': self.request_info['requestId'],
                'transactionId': self.request_info['transactionId'],
                'requestStatus': 'error',
                'statusMessage': error_message}

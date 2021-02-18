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
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import error_log
from osdf.utils.interfaces import get_rest_client
from requests import RequestException
from threading import Thread
import traceback
BASE_DIR = os.path.dirname(__file__)


# This is the class for NST Selection


class NstSelection(Thread):

    def __init__(self, osdf_config, slice_config, request_json, model_type):
        super().__init__()
        self.osdf_config = osdf_config
        self.slice_config = slice_config
        self.request_json = request_json
        self.model_type = model_type
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
            # solution = self.get_nst_selection_response(solution)
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
        req_info = self.request_json['requestInfo']
        requirements = self.request_json['serviceProfile']['serviceProfileParameters']
        model_name = "nst"
        policies = self.get_app_policies(model_name, "nst_selection")
        config_input_json = os.path.join(BASE_DIR, 'conf/configIinputs.json')

        conductor_response = self.get_conductor(req_info, requirements, policies, model_name)
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

        # return nst_solution_list
        return conductor_response

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

    def get_app_policies(self, model_name, app_name):
        policy_request_json = self.request_json.copy()
        policy_request_json['serviceInfo'] = {'serviceName': model_name}
        if 'serviceProfile' in self.request_json:
            slice_scope = self.request_json['serviceProfile']['serviceProfileParameters']['resourceSharingLevel']
            if 'preferReuse' in self.request_json and slice_scope == "shared":
                slice_scope = slice_scope + "," + ("reuse" if self.request_json['preferReuse'] else "create_new")
            policy_request_json['slice_scope'] = slice_scope
        debug_log.debug("policy_request_json {}".format(str(policy_request_json)))
        return get_policies(policy_request_json, app_name)  # app_name: nst_selection

    def get_conductor(self, req_info, request_parameters, policies, model_name):
        demands = [
            {
                "resourceModuleName": model_name,
                "resourceModelInfo": {}
            }
        ]

        try:
            template_fields = {
                'location_enabled': False,
                'version': '2020-08-13'
            }
            resp = conductor.request(req_info, demands, request_parameters, {}, template_fields,
                                     self.osdf_config, policies)
        except RequestException as e:
            resp = e.response.json()
            error = resp['plans'][0]['message']
            if "Unable to find any" in error:
                return self.get_nst_selection_response([])
            error_log.error('Error from conductor {}'.format(error))
            return self.error_response(error)
        debug_log.debug("Response from conductor in get_conductor method {}".format(str(resp)))
        recommendations = resp["plans"][0].get("recommendations")
        return self.process_response(recommendations, model_name)

    def process_response(self, recommendations, model_name):
        """Process conductor response to form the response for the API request

            :param recommendations: recommendations from conductor
            :return: response json as a dictionary
        """
        if not recommendations:
            return self.get_nst_selection_response([])
        solutions = [self.get_solution_from_candidate(rec[model_name]['candidate'])
                     for rec in recommendations]
        return self.get_nst_selection_response(solutions)

    def get_solution_from_candidate(self, candidate):
        if candidate['inventory_type'] == 'nst':
            return {
                'UUID': candidate['candidate_id'],
                'invariantUUID': candidate['model_invariant_id'],
                'NSTName': candidate['name'],
            }

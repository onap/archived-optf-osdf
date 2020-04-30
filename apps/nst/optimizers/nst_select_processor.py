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
import traceback
from requests import RequestException
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.logging.osdf_logging import error_log, debug_log
"""
This application generates NST SELECTION API calls using the information received from SO
"""

def get_nst_demands(model_name):
    """
    :param model_name: NST
    """
    nst_slice_demand = dict()
    nst_slice_demands = list()
    nst_slice_demand["resourceModuleName"] = model_name
    nst_slice_demands.append((nst_slice_demand))
    return nst_slice_demands

def get_nst_solution(request_json, osdf_config):
    """Process the nst selection request from API layer
        :param request_json: api request
        :param osdf_config: configuration specific to OSDF app
        :return: response as a dictionary
        """
    req_info = request_json['requestInfo']
    try:

        overall_recommendations = dict()
        nst_name = "NST"
        policies = get_policies(request_json, "nst_selection")
        demands = get_nst_demands(nst_name)
        request_parameters = request_json.get("serviceProfile")
        service_info = {}
        req_info['numSolutions'] = 'all'
        resp = conductor.request(req_info, demands, request_parameters, service_info, False,
                                osdf_config, policies)
        overall_recommendations[nst_name] = resp["plans"][0].get("recommendations")

        return conductor_response_processor_for_nst(overall_recommendations, req_info)

    except Exception as ex:
        error_log.error("Error for {} {}".format(req_info.get('requestId'),
                                                 traceback.format_exc()))
        if isinstance(ex, RequestException):
            try:
                error_message = json.loads(ex.response)['plans'][0]['message']
            except Exception:
                error_message = "Problem connecting to conductor"
        else:
            error_message = str(ex)
        return error_message






def process_nst_selection( request_json, osdf_config):
    """
    Process a PCI request from a Client (build config-db, policy and  API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :return: response from NST Opt
    """
    solution = get_nst_solution(request_json, osdf_config)

    return {
        "requestId" : request_json['requestInfo']['requestId'],
        "transactionId" : request_json['requestInfo']['transactionId'],
        "statusMessage" : " ",
        "requestStatus" : "accepted",
        "solutions" : solution
    }

def conductor_response_processor_for_nst(overall_recommendations, request_info):
    """Process conductor response to form the response for the API request
        :param overall_recommendations: recommendations from conductor
        :param request_info: request info
        :return: response json as a dictionary
    """
    nstSolutionList = []
    for nst_name, recommendations in overall_recommendations.items():
        for recommendation in recommendations:
            nst_solutions = dict()
            nst_solutions["invariantUUID"] = recommendation.get('NST').get("modelinvariantuuid")
            nst_solutions["UUID"] = recommendation.get('NST').get("modeluuid")
            nst_solutions["NSTName"] = recommendation.get('NST').get('candidate_id')
            nst_solutions["matchLevel"] = 1
            nstSolutionList.append(nst_solutions)

    return nstSolutionList
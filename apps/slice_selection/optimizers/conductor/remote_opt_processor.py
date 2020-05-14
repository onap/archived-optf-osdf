# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
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

"""
Module for processing slice selection request
"""

import json
import traceback
from requests import RequestException

from apps.slice_selection.optimizers.conductor.response_processor \
    import conductor_response_processor, conductor_error_response_processor, solution_with_only_slice_profile, get_nsi_selection_response
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.adapters.policy.utils import group_policies_gen
from osdf.logging.osdf_logging import error_log, debug_log
from osdf.utils.mdc_utils import mdc_from_json


def process_nsi_selection_opt(request_json, osdf_config):
    """Process the nsi selection request from API layer
        :param request_json: api request
        :param policies: flattened policies corresponding to this request
        :param osdf_config: configuration specific to OSDF app
        :return: response as a dictionary
        """
    req_info = request_json['requestInfo']
    try:
        mdc_from_json(request_json)

        overall_recommendations = dict()
        nst_info_map = dict()
        new_nsi_solutions = list()
        for nst_info in request_json["NSTInfoList"]:
            nst_name = nst_info["modelName"]
            nst_info_map[nst_name] =  {"NSTName": nst_name,
                                                    "UUID": nst_info["modelVersionId"],
                                                    "invariantUUID": nst_info["modelInvariantId"]}

            if request_json["serviceProfile"]["resourceSharingLevel"] == "non-shared":
                new_nsi_solution = solution_with_only_slice_profile(request_json['serviceProfile'], nst_info_map.get(nst_name))
                new_nsi_solutions.append(new_nsi_solution)
            else:
                policy_request_json = request_json.copy()
                policy_request_json['serviceInfo']['serviceName'] = nst_name
                policies = get_policies(policy_request_json, "slice_selection")

                demands = get_slice_demands(nst_name, policies, osdf_config.core)

                request_parameters = request_json.get('serviceProfile',{})
                service_info = {}
                req_info['numSolutions'] = 'all'
                try:
                    resp = conductor.request(req_info, demands, request_parameters, service_info, False,
                                             osdf_config, policies)
                except RequestException as e:
                    resp = e.response.json()
                    error = resp['plans'][0]['message']
                    error_log.error('Error from conductor {}'.format(error))
                debug_log.debug("Response from conductor {}".format(str(resp)))
                overall_recommendations[nst_name] = resp["plans"][0].get("recommendations")

        if request_json["serviceProfile"]["resourceSharingLevel"] == "non-shared":
            solutions = dict()
            solutions['newNSISolutions'] = new_nsi_solutions
            solutions['sharedNSISolutions'] = []
            return get_nsi_selection_response(req_info, solutions)
        else:
            return conductor_response_processor(overall_recommendations, nst_info_map, req_info, request_json["serviceProfile"])
    except Exception as ex:
        error_log.error("Error for {} {}".format(req_info.get('requestId'),
                                                 traceback.format_exc()))
        error_message = str(ex)
        return conductor_error_response_processor(req_info, error_message)


def get_slice_demands(model_name, policies, config):
    """
    :param model_name: model name of the slice
    :param policies: flattened polcies corresponding to the request
    :param config: configuration specific to OSDF app
    :return: list of demands for the request
    """
    group_policies = group_policies_gen(policies, config)
    subscriber_policy_list = group_policies["onap.policies.optimization.service.SubscriberPolicy"]
    slice_demands = list()
    for subscriber_policy in subscriber_policy_list:
        policy_properties = subscriber_policy[list(subscriber_policy.keys())[0]]['properties']
        if model_name in policy_properties["services"]:
            for subnet in policy_properties["properties"]["subscriberName"]:
                slice_demand = dict()
                slice_demand["resourceModuleName"] = subnet
                slice_demand['resourceModelInfo'] = {}
                slice_demands.append(slice_demand)
    return slice_demands

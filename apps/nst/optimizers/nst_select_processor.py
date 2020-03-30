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
from apps.slice_selection.optimizers.conductor.response_processor \
    import conductor_response_processor, conductor_error_response_processor, conductor_response_processor_for_nst
from requests import RequestException
from osdf.adapters.policy.utils import group_policies_gen
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.logging.osdf_logging import error_log, debug_log
"""
This application generates NST SELECTION API calls using the information received from SO
"""

def get_nst_demands(model_name, policies, config):
    """
    :param model_name: model name of the slice
    :param policies: flattened polcies corresponding to the request
    :param config: configuration specific to OSDF app
    :return: list of demands for the request
    """
    group_policies = group_policies_gen(policies, config)
    subscriber_policy_list = group_policies["onap.policies.optimization.SubscriberPolicy"]
    slice_demands = list()
    for subscriber_policy in subscriber_policy_list:
        policy_properties = subscriber_policy[list(subscriber_policy.keys())[0]]['properties']
        if model_name in policy_properties["services"]:
            subnet_attributes = policy_properties["properties"]["subscriberRole"][0]
            for subnet in policy_properties["properties"]["subscriberName"]:
                slice_demand = dict()
                slice_demand["resourceModuleName"] = subnet
                slice_demand['resourceModelInfo'] = subnet_attributes[subnet]
                slice_demands.append(slice_demand)
    return slice_demands

def getNSTSolution(request_json, osdf_config):
    """Process the nst selection request from API layer
        :param request_json: api request
        :param policies: flattened policies corresponding to this request
        :param osdf_config: configuration specific to OSDF app
        :return: response as a dictionary
        """
    req_info = request_json['requestInfo']
    try:

        overall_recommendations = dict()
        nst_info_map = dict()
        nst_name = "NST"
        nst_info_map["nst_name"] = {"NSTName": nst_name,
                                        "UUID": request_json["serviceProfile"]["serviceProfileParameters"]["modelVersionId"],
                                        "invariantUUID":request_json["serviceProfile"]["serviceProfileParameters"]["modelInvariantId"]}

        policy_request_json = request_json.copy()
        policy_request_json["serviceProfile"]['serviceProfileParameters']['serviceName'] = nst_name

        policies = get_policies(policy_request_json, "nst_selection")

        demands = get_nst_demands(nst_name, policies, osdf_config.core)

        request_parameters = {}
        service_info = {}
        req_info['numSolutions'] = 'all'
        resp = conductor.request(req_info, demands, request_parameters, service_info, False,
                                osdf_config, policies)
        overall_recommendations[nst_name] = resp["plans"][0].get("recommendations")

        return conductor_response_processor_for_nst(overall_recommendations, nst_info_map, req_info)

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
        return conductor_error_response_processor(req_info, error_message)






def process_nst_selection( request_json, osdf_config):
    """
    Process a PCI request from a Client (build config-db, policy and  API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :return: response from NST Opt
    """
    return getNSTSolution(request_json, osdf_config)

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

import traceback
from requests import RequestException

from apps.slice_selection.optimizers.conductor import utils
from apps.slice_selection.optimizers.conductor.response_processor import conductor_response_processor
from apps.slice_selection.optimizers.conductor.response_processor import conductor_error_response_processor
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.logging.osdf_logging import error_log, debug_log
from osdf.utils.mdc_utils import mdc_from_json


def process_nsi_selection_opt(request_json, osdf_config):
    """Process the nsi selection request from API layer
        :param request_json: api request
        :param osdf_config: configuration specific to OSDF app
        :return: response as a dictionary
        """
    req_info = request_json['requestInfo']
    try:
        mdc_from_json(request_json)
        overall_recommendations = dict()
        resp, nst_info = call_to_conductor(request_json, osdf_config, 'NSI')
        debug_log.debug("Response from conductor {}".format(str(resp)))
        overall_recommendations[nst_info['name']] = resp["plans"][0].get("recommendations")
        return conductor_response_processor(overall_recommendations, nst_info, req_info, request_json["serviceProfile"])
    except Exception as ex:
        error_log.error("Error for {} {}".format(req_info.get('requestId'),
                                                 traceback.format_exc()))
        error_message = str(ex)
        return conductor_error_response_processor(req_info, error_message)


def process_nssi_selection_opt(request_json, osdf_config):
    """Process the nssi selection request from API layer
        :param request_json: api request
        :param osdf_config: configuration specific to OSDF app
        :return: response as a dictionary
        """
    req_info = request_json['requestInfo']
    if request_json['sliceProfile']['resourceSharingLevel'] == 'shared':
        try:
            mdc_from_json(request_json)
            overall_recommendations = dict()
            resp, nsst_info = call_to_conductor(request_json, osdf_config, 'NSI')
            debug_log.debug("Response from conductor {}".format(str(resp)))
            overall_recommendations[nsst_info['name']] = resp["plans"][0].get("recommendations")
            return conductor_response_processor(overall_recommendations, nsst_info, req_info,
                                                request_json["sliceProfile"])
        except Exception as ex:
            error_log.error("Error for {} {}".format(req_info.get('requestId'),
                                                     traceback.format_exc()))
            error_message = str(ex)
            return conductor_error_response_processor(req_info, error_message)
    elif request_json['sliceProfile']['resourceSharingLevel'] == 'not-shared':
        solutions = []


def get_request_parameters(request_json, nxi):
    request_params = utils.convert_to_snake_case(request_json.get('serviceProfile', {}) if nxi == "NSI"
                                                 else request_json.get('sliceProfile', {}))
    subnet_capabilities = request_json['subnetCapabilities']
    if subnet_capabilities:
        for subnet_capability in subnet_capabilities:
            domain_type = f"{subnet_capability['domainType'].lower().replace('-', '_')}_"
            capability_details = subnet_capability['capabilityDetails']
            for key, value in capability_details.items():
                request_params[f"{domain_type}{utils.CAMEL_TO_SNAKE[key]}"] = value
    return request_params


def get_demand_structure(demand_name):
    demands = []
    demand = dict()
    demand["resourceModuleName"] = demand_name
    demand['resourceModelInfo'] = {}
    demands.append(demand)
    return demands


def call_to_conductor(request_json, osdf_config, nxi):
    req_info = request_json['requestInfo']
    service_info = {}
    nxt_info = {}

    if nxi == 'NSI':
        nxt_info = request_json["NSTInfo"]
    elif nxi == 'NSSI':
        nxt_info = request_json["NSSTInfo"]

    request_parameters = get_request_parameters(request_json, nxi)
    nxt_name = nxt_info['name']
    demands = get_demand_structure(nxt_name)
    policy_request_json = request_json.copy()
    policy_request_json['serviceInfo'] = {'serviceName': nxt_name}
    policies = get_policies(policy_request_json, "slice_selection") if nxi == 'NSI' \
        else get_policies(policy_request_json, "subnet_selection")
    try:
        resp = conductor.request(req_info, demands, request_parameters, service_info, False, osdf_config,
                                 policies)
    except RequestException as e:
        resp = e.response.json()
        error = resp['plans'][0]['message']
        error_log.error('Error from conductor {}'.format(error))
    return resp, nxt_info

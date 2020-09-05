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

from requests import RequestException
import traceback

from apps.slice_selection.optimizers.conductor.response_processor import conductor_error_response_processor
from apps.slice_selection.optimizers.conductor.response_processor import conductor_response_processor
from apps.slice_selection.optimizers.conductor import utils
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import error_log
from osdf.utils.interfaces import get_rest_client
from osdf.utils.mdc_utils import mdc_from_json


APP_INFO = {
    'NSI': {
        'app_name': 'slice_selection',
        'requirements_field': 'serviceProfile',
        'model_info': 'NSTInfo'
    },
    'NSSI': {
        'app_name': 'subnet_selection',
        'requirements_field': 'sliceProfile',
        'model_info': 'NSSTInfo'
    }
}


def process_slice_selection_opt(request_json, osdf_config, model_type):
    """Process the slice selection request from the API layer

        :param request_json: api request
        :param osdf_config: configuration specific to OSDF app
        :param model_type: type of the slice, NSI/NSSI
        :return: response as a dictionary
    """
    req_info = request_json['requestInfo']
    rc = get_rest_client(request_json, service='so')

    try:
        if model_type == 'NSSI' and request_json['sliceProfile']['resourceSharingLevel'] == 'not-shared':
            message = "Slice selection for non-shared slice is not supported"
            final_response = conductor_error_response_processor(req_info, message)

        else:
            final_response = do_slice_selection(request_json, model_type, osdf_config)

    except Exception as ex:
        error_log.error("Error for {} {}".format(req_info.get('requestId'),
                                                 traceback.format_exc()))
        error_message = str(ex)
        final_response = conductor_error_response_processor(req_info, error_message)

    try:
        rc.request(json=final_response, noresponse=True)
    except RequestException:
        error_log.error("Error sending asynchronous notification for {} {}".format(req_info['request_id'],
                                                                                   traceback.format_exc()))


def do_slice_selection(request_json, model_type, osdf_config):
    req_info = request_json['requestInfo']
    app_info = APP_INFO[model_type]
    mdc_from_json(request_json)
    requirements = request_json.get(app_info['requirements_field'], {})
    model_info = request_json.get(app_info['model_info'])
    model_name = model_info['name']
    policies = get_app_policies(request_json, model_name, app_info['app_name'])
    request_parameters = get_request_parameters(request_json, requirements)

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
                                 osdf_config, policies)
    except RequestException as e:
        resp = e.response.json()
        error = resp['plans'][0]['message']
        error_log.error('Error from conductor {}'.format(error))
        return conductor_error_response_processor(req_info, error)

    debug_log.debug("Response from conductor {}".format(str(resp)))
    recommendations = resp["plans"][0].get("recommendations")
    subnets = [subnet['domainType'] for subnet in request_json['subnetCapabilities']] \
        if request_json.get('subnetCapabilities') else []
    return conductor_response_processor(recommendations, model_info, subnets, req_info)


def get_request_parameters(request_json, requirements):
    request_params = utils.convert_to_snake_case(requirements)
    subnet_capabilities = request_json.get('subnetCapabilities')
    if subnet_capabilities:
        for subnet_capability in subnet_capabilities:
            domain_type = f"{subnet_capability['domainType'].lower().replace('-', '_')}_"
            capability_details = subnet_capability['capabilityDetails']
            for key, value in capability_details.items():
                request_params[f"{domain_type}{utils.CAMEL_TO_SNAKE[key]}"] = value
    return request_params


def get_app_policies(request_json, model_name, app_name):
    policy_request_json = request_json.copy()
    policy_request_json['serviceInfo'] = {'serviceName': model_name}
    if 'preferReuse' in request_json:
        policy_request_json['preferReuse'] = "reuse" if request_json['preferReuse'] else "create_new"
    return get_policies(policy_request_json, app_name)

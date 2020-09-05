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
from threading import Thread
import traceback

from apps.slice_selection.optimizers.conductor.response_processor import ResponseProcessor
from osdf.adapters.conductor import conductor
from osdf.adapters.policy.interface import get_policies
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import error_log
from osdf.utils.interfaces import get_rest_client
from osdf.utils.mdc_utils import mdc_from_json


class SliceSelectionOptimizer(Thread):
    def __init__(self, osdf_config, slice_config, request_json, model_type):
        self.osdf_config = osdf_config
        self.slice_config = slice_config
        self.request_json = request_json
        self.model_type = model_type
        self.response_processor = ResponseProcessor(request_json['requestInfo'], slice_config)

    def run(self):
        self.process_slice_selection_opt()

    def process_slice_selection_opt(self):
        """Process the slice selection request from the API layer"""
        req_info = self.request_json['requestInfo']
        rc = get_rest_client(self.request_json, service='so')

        try:
            if self.model_type == 'NSSI' and self.request_json['sliceProfile']['resourceSharingLevel'] == 'not-shared':
                message = "Slice selection for non-shared slice is not supported"
                final_response = self.response_processor.process_error_response(message)

            else:
                final_response = self.do_slice_selection()

        except Exception as ex:
            error_log.error("Error for {} {}".format(req_info.get('requestId'),
                                                     traceback.format_exc()))
            error_message = str(ex)
            final_response = self.response_processor.process_error_response(error_message)

        try:
            rc.request(json=final_response, noresponse=True)
        except RequestException:
            error_log.error("Error sending asynchronous notification for {} {}".format(req_info['request_id'],
                                                                                       traceback.format_exc()))

    def do_slice_selection(self):
        req_info = self.request_json['requestInfo']
        app_info = self.slice_config['app_info'][self.model_type]
        mdc_from_json(self.request_json)
        requirements = self.request_json.get(app_info['requirements_field'], {})
        model_info = self.request_json.get(app_info['model_info'])
        model_name = model_info['name']
        policies = self.get_app_policies(model_name, app_info['app_name'])
        request_parameters = self.get_request_parameters(requirements)

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
            error_log.error('Error from conductor {}'.format(error))
            return self.response_processor.process_error_response(error)

        debug_log.debug("Response from conductor {}".format(str(resp)))
        recommendations = resp["plans"][0].get("recommendations")
        subnets = [subnet['domainType'] for subnet in self.request_json['subnetCapabilities']] \
            if self.request_json.get('subnetCapabilities') else []
        return self.response_processor.process_response(recommendations, model_info, subnets)

    def get_request_parameters(self, requirements):
        camel_to_snake = self.slice_config['attribute_mapping']['camel_to_snake']
        request_params = {camel_to_snake[key]: value for key, value in requirements.items()}
        subnet_capabilities = self.request_json.get('subnetCapabilities')
        if subnet_capabilities:
            for subnet_capability in subnet_capabilities:
                domain_type = f"{subnet_capability['domainType'].lower().replace('-', '_')}_"
                capability_details = subnet_capability['capabilityDetails']
                for key, value in capability_details.items():
                    request_params[f"{domain_type}{camel_to_snake[key]}"] = value
        return request_params

    def get_app_policies(self, model_name, app_name):
        policy_request_json = self.request_json.copy()
        policy_request_json['serviceInfo'] = {'serviceName': model_name}
        if 'preferReuse' in self.request_json:
            policy_request_json['preferReuse'] = "reuse" if self.request_json['preferReuse'] else "create_new"
        return get_policies(policy_request_json, app_name)

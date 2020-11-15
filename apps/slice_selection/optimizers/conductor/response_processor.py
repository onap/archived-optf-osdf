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
Module for processing response from conductor for slice selection
"""

import re


class ResponseProcessor(object):
    def __init__(self, request_info, slice_config):
        self.request_info = request_info
        self.slice_config = slice_config

    def process_response(self, recommendations, model_info, subnets):
        """Process conductor response to form the response for the API request

            :param recommendations: recommendations from conductor
            :param model_info: model info from the request
            :param subnets: list of subnets
            :return: response json as a dictionary
        """
        if not recommendations:
            return self.get_slice_selection_response([])
        model_name = model_info['name']
        solutions = [self.get_solution_from_candidate(rec[model_name]['candidate'], model_info, subnets)
                     for rec in recommendations]
        return self.get_slice_selection_response(solutions)

    def get_solution_from_candidate(self, candidate, model_info, subnets):
        if candidate['inventory_type'] == 'nssi':
            return {
                'UUID': model_info['UUID'],
                'invariantUUID': model_info['invariantUUID'],
                'NSSIName': candidate['instance_name'],
                'NSSIId': candidate['instance_id']
            }

        elif candidate['inventory_type'] == 'nsi':
            return {
                'existingNSI': True,
                'sharedNSISolution': {
                    'UUID': model_info['UUID'],
                    'invariantUUID': model_info['invariantUUID'],
                    'NSIName': candidate['instance_name'],
                    'NSIId': candidate['instance_id']
                }
            }

        elif candidate['inventory_type'] == 'slice_profiles':
            return {
                'existingNSI': False,
                'newNSISolution': {
                    'sliceProfiles': self.get_slice_profiles_from_candidate(candidate, subnets)
                }
            }

    def get_slice_profiles_from_candidate(self, candidate, subnets):
        slice_profiles = []
        for subnet in subnets:
            slice_profile = {self.get_profile_attribute(k, subnet): v for k, v in candidate.items()
                             if k.startswith(subnet)}
            slice_profile['domainType'] = subnet
            slice_profiles.append(slice_profile)
        return slice_profiles

    def get_profile_attribute(self, attribute, subnet):
        snake_to_camel = self.slice_config['attribute_mapping']['snake_to_camel']
        return snake_to_camel[re.sub(f'^{subnet}_', '', attribute)]

    def process_error_response(self, error_message):
        """Form response message from the error message

            :param error_message: error message while processing the request
            :return: response json as dictionary
        """
        return {'requestId': self.request_info['requestId'],
                'transactionId': self.request_info['transactionId'],
                'requestStatus': 'error',
                'statusMessage': error_message}

    def get_slice_selection_response(self, solutions):
        """Get NSI selection response from final solution

            :param solutions: final solutions
            :return: NSI selection response to send back as dictionary
        """
        return {'requestId': self.request_info['requestId'],
                'transactionId': self.request_info['transactionId'],
                'requestStatus': 'completed',
                'statusMessage': '',
                'solutions': solutions}

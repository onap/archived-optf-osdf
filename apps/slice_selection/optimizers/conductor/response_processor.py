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


SLICE_PROFILE_FIELDS = {"latency": "latency",
                        "max_number_of_ues": "maxNumberOfUEs",
                        "coverage_area_ta_list": "coverageAreaTAList",
                        "ue_mobility_level": "uEMobilityLevel",
                        "resource_sharing_level": "resourceSharingLevel",
                        "exp_data_rate_ul": "expDataRateUL",
                        "exp_data_rate_dl": "expDataRateDL",
                        "area_traffic_cap_ul": "areaTrafficCapUL",
                        "area_traffic_cap_dl": "areaTrafficCapDL",
                        "activity_factor": "activityFactor",
                        "e2e_latency": "e2eLatency",
                        "jitter": "jitter",
                        "survival_time": "survivalTime",
                        "exp_data_rate": "expDataRate",
                        "payload_size": "payloadSize",
                        "traffic_density": "trafficDensity",
                        "conn_density": "connDensity",
                        "reliability": "reliability",
                        "service_area_dimension": "serviceAreaDimension",
                        "cs_availability": "csAvailability"
                        }


def conductor_response_processor(recommendations, model_info, subnets, request_info):
    """Process conductor response to form the response for the API request

        :param recommendations: recommendations from conductor
        :param model_info: model info from the request
        :param subnets: list of subnets
        :param request_info: request info
        :return: response json as a dictionary
    """
    if not recommendations:
        return get_slice_selection_response(request_info, [])
    model_name = model_info['name']
    solutions = [get_solution_from_candidate(rec[model_name]['candidate'], model_info, subnets)
                 for rec in recommendations]
    return get_slice_selection_response(request_info, solutions)


def get_solution_from_candidate(candidate, model_info, subnets):
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
                'slice_profiles': get_slice_profiles_from_candidate(candidate, subnets)
            }
        }


def get_slice_profiles_from_candidate(candidate, subnets):
    slice_profiles = []
    for subnet in subnets:
        slice_profile = {get_profile_attribute(k, subnet): v for k, v in candidate.items() if k.startswith(subnet)}
        slice_profile['domainType'] = subnet
        slice_profiles.append(slice_profile)
    return slice_profiles


def get_profile_attribute(attribute, subnet):
    return SLICE_PROFILE_FIELDS[re.sub(f'^{subnet}_', '', attribute)]


def conductor_error_response_processor(request_info, error_message):
    """Form response message from the error message

        :param request_info: request info
        :param error_message: error message while processing the request
        :return: response json as dictionary
    """
    return {'requestId': request_info['requestId'],
            'transactionId': request_info['transactionId'],
            'requestStatus': 'error',
            'statusMessage': error_message}


def get_slice_selection_response(request_info, solutions):
    """Get NSI selection response from final solution

        :param request_info: request info
        :param solutions: final solutions
        :return: NSI selection response to send back as dictionary
    """
    return {'requestId': request_info['requestId'],
            'transactionId': request_info['transactionId'],
            'requestStatus': 'completed',
            'statusMessage': '',
            'solutions': solutions}

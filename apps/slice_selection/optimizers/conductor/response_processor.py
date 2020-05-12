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

from osdf.logging.osdf_logging import debug_log


SLICE_PROFILE_FIELDS = {"latency":"latency", "max_number_of_ues":"maxNumberOfUEs", "coverage_area_ta_list": "coverageAreaTAList",
                        "ue_mobility_level":"uEMobilityLevel", "resource_sharing_level":"resourceSharingLevel", "exp_data_rate_ul": "expDataRateUL",
                        "exp_data_rate_dl":"expDataRateDL", "area_traffic_cap_ul":"areaTrafficCapUL", "area_traffic_cap_dl": "areaTrafficCapDL",
                        "activity_factor":"activityFactor", "e2e_latency":"e2eLatency", "jitter":"jitter", "survival_time": "survivalTime",
                        "exp_data_rate":"expDataRate", "payload_size":"payloadSize", "traffic_density":"trafficDensity", "conn_density":"connDensity",
                        "reliability":"reliability", "service_area_dimension":"serviceAreaDimension", "cs_availability": "csAvailability"}


def conductor_response_processor(overall_recommendations, nst_info_map, request_info, service_profile):
    """Process conductor response to form the response for the API request
        :param overall_recommendations: recommendations from conductor
        :param nst_info_map: NST info from the request
        :param request_info: request info
        :return: response json as a dictionary
    """
    shared_nsi_solutions = list()
    new_nsi_solutions = list()
    for nst_name, recommendations in overall_recommendations.items():
        if  not (recommendations):
            new_nsi_solution = solution_with_only_slice_profile(service_profile, nst_info_map.get(nst_name))
            new_nsi_solutions.append(new_nsi_solution)
            continue

        for recommendation in recommendations:
            nsi_set = set(values['candidate']['nsi_id'] for key, values in recommendation.items())
            if len(nsi_set) == 1:
                nsi_id = nsi_set.pop()
                candidate = list(recommendation.values())[0]['candidate']
                debug_log.debug("The NSSIs in the solution belongs to the same NSI {}"
                                .format(nsi_id))
                shared_nsi_solution = dict()
                shared_nsi_solution["NSIId"] = nsi_id
                shared_nsi_solution["NSIName"] = candidate.get('nsi_name')
                shared_nsi_solution["UUID"] = candidate.get('nsi_model_version_id')
                shared_nsi_solution["invariantUUID"] = candidate.get('nsi_model_invariant_id')

                nssi_info_list = get_nssi_solutions(recommendation)
                nssis = list()
                for nssi_info in nssi_info_list:
                    nssi = dict()
                    nssi["NSSIId"] = nssi_info.get("NSSISolution").get("NSSIId")
                    nssi["NSSIName"] = nssi_info.get("NSSISolution").get("NSSIName")
                    nssi["UUID"] = ""
                    nssi["invariantUUID"] = ""
                    nssi["sliceProfile"] = [nssi_info.get("sliceProfile")]
                    nssis.append(nssi)

                shared_nsi_solution["NSSIs"] = nssis
                shared_nsi_solutions.append(shared_nsi_solution)
            else:
                nssi_solutions = get_nssi_solutions(recommendation)
                new_nsi_solution = dict()
                new_nsi_solution['matchLevel'] = ""
                new_nsi_solution['NSTInfo'] = nst_info_map.get(nst_name)
                new_nsi_solution['NSSISolutions'] = nssi_solutions
                new_nsi_solutions.append(new_nsi_solution)

    solutions = dict()
    solutions['sharedNSISolutions'] = shared_nsi_solutions
    solutions['newNSISolutions'] = new_nsi_solutions
    return get_nsi_selection_response(request_info, solutions)


def solution_with_only_slice_profile(service_profile, nst_info):
    nssi_solutions = get_slice_profile_from_service_profile(service_profile)
    new_nsi_solution = dict()
    new_nsi_solution['matchLevel'] = ""
    new_nsi_solution['NSTInfo'] = nst_info
    new_nsi_solution['NSSISolutions'] = nssi_solutions
    return new_nsi_solution

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


def get_slice_profile_from_service_profile(service_profile):
    nssi_solutions = list()
    service_profile["domainType"] = "cn"
    nssi_solution = {"sliceProfile": service_profile}
    nssi_solutions.append(nssi_solution)
    return nssi_solutions


def get_nssi_solutions(recommendation):
    """Get nssi solutions from recommendation
        :param recommendation: recommendation from conductor
        :return: new nssi solutions list
    """
    nssi_solutions = list()

    for nsst_name, nsst_rec in recommendation.items():
        candidate = nsst_rec['candidate']
        nssi_info, slice_profile = get_solution_from_candidate(candidate)
        nsst_info = {"NSSTName": nsst_name}
        nssi_solution = {"sliceProfile": slice_profile,
                         "NSSTInfo": nsst_info,
                         "NSSISolution": nssi_info}
        nssi_solutions.append(nssi_solution)
    return nssi_solutions


def get_solution_from_candidate(candidate):
    """Get nssi info from candidate
        :param candidate: Candidate from the recommendation
        :return: nssi_info and slice profile derived from candidate
    """
    slice_profile = dict()
    nssi_info = {"NSSIName": candidate['instance_name'],
                 "NSSIId": candidate['candidate_id']}

    for field in SLICE_PROFILE_FIELDS:
        if candidate[field]:
            slice_profile[SLICE_PROFILE_FIELDS[field]] = candidate[field]

    return nssi_info, slice_profile


def get_nsi_selection_response(request_info, solutions):
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


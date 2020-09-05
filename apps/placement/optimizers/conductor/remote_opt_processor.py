# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

from jinja2 import Template
import json
from requests import RequestException
import traceback

from apps.license.optimizers.simple_license_allocation import license_optim
from osdf.adapters.conductor import conductor
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import error_log
from osdf.logging.osdf_logging import metrics_log
from osdf.logging.osdf_logging import MH
from osdf.operation.error_handling import build_json_error_body
from osdf.utils.interfaces import get_rest_client
from osdf.utils.mdc_utils import mdc_from_json


def conductor_response_processor(conductor_response, req_id, transaction_id):
    """Build a response object to be sent to client's callback URL from Conductor's response

    This includes Conductor's placement optimization response, and required ASDC license artifacts
    :param conductor_response: JSON response from Conductor
    :param raw_response: Raw HTTP response corresponding to above
    :param req_id: Id of a request
    :return: JSON object that can be sent to the client's callback URL
    """
    composite_solutions = []
    name_map = {"physical-location-id": "cloudClli", "host_id": "vnfHostName",
                "cloud_version": "cloudVersion", "cloud_owner": "cloudOwner",
                "cloud": "cloudRegionId", "service": "serviceInstanceId", "is_rehome": "isRehome",
                "location_id": "locationId", "location_type": "locationType", "directives": "oof_directives"}
    for reco in conductor_response['plans'][0]['recommendations']:
        for resource in reco.keys():
            c = reco[resource]['candidate']
            solution = {
                'resourceModuleName': resource,
                'serviceResourceId': reco[resource].get('service_resource_id', ""),
                'solution': {"identifierType": name_map.get(c['inventory_type'], c['inventory_type']),
                             'identifiers': [c['candidate_id']],
                             'cloudOwner': c.get('cloud_owner', "")},
                'assignmentInfo': []
            }
            for key, value in c.items():
                if key in ["location_id", "location_type", "is_rehome", "host_id"]:
                    try:
                        solution['assignmentInfo'].append({"key": name_map.get(key, key), "value": value})
                    except KeyError:
                        debug_log.debug("The key[{}] is not mapped and will not be returned in assignment info"
                                        .format(key))

            for key, value in reco[resource]['attributes'].items():
                try:
                    solution['assignmentInfo'].append({"key": name_map.get(key, key), "value": value})
                except KeyError:
                    debug_log.debug("The key[{}] is not mapped and will not be returned in assignment info"
                                    .format(key))
            composite_solutions.append(solution)

    request_status = "completed" if conductor_response['plans'][0]['status'] == "done" \
        else conductor_response['plans'][0]['status']
    status_message = conductor_response.get('plans')[0].get('message', "")

    solution_info = {}
    if composite_solutions:
        solution_info.setdefault('placementSolutions', [])
        solution_info['placementSolutions'].append(composite_solutions)

    resp = {
        "transactionId": transaction_id,
        "requestId": req_id,
        "requestStatus": request_status,
        "statusMessage": status_message,
        "solutions": solution_info
    }
    return resp


def conductor_no_solution_processor(conductor_response, request_id, transaction_id,
                                    template_placement_response="templates/plc_opt_response.jsont"):
    """Build a response object to be sent to client's callback URL from Conductor's response

    This is for case where no solution is found
    :param conductor_response: JSON response from Conductor
    :param raw_response: Raw HTTP response corresponding to above
    :param request_id: request Id associated with the client request (same as conductor response's "name")
    :param template_placement_response: the template for generating response to client (plc_opt_response.jsont)
    :return: JSON object that can be sent to the client's callback URL
    """
    status_message = conductor_response["plans"][0].get("message")
    templ = Template(open(template_placement_response).read())
    return json.loads(templ.render(composite_solutions=[], requestId=request_id, license_solutions=[],
                                   transactionId=transaction_id,
                                   requestStatus="completed", statusMessage=status_message, json=json))


def process_placement_opt(request_json, policies, osdf_config):
    """Perform the work for placement optimization (e.g. call SDC artifact and make conductor request)

    NOTE: there is scope to make the requests to policy asynchronous to speed up overall performance
    :param request_json: json content from original request
    :param policies: flattened policies corresponding to this request
    :param osdf_config: configuration specific to OSDF app
    :param prov_status: provStatus retrieved from Subscriber policy
    :return: None, but make a POST to callback URL
    """

    try:
        mdc_from_json(request_json)
        rc = get_rest_client(request_json, service="so")
        req_id = request_json["requestInfo"]["requestId"]
        transaction_id = request_json['requestInfo']['transactionId']

        metrics_log.info(MH.inside_worker_thread(req_id))
        license_info = None
        if request_json.get('licenseInfo', {}).get('licenseDemands'):
            license_info = license_optim(request_json)

        # Conductor only handles placement, only call Conductor if placementDemands exist
        if request_json.get('placementInfo', {}).get('placementDemands'):
            metrics_log.info(MH.requesting("placement/conductor", req_id))
            req_info = request_json['requestInfo']
            demands = request_json['placementInfo']['placementDemands']
            request_parameters = request_json['placementInfo']['requestParameters']
            service_info = request_json['serviceInfo']
            template_fields = {
                'location_enabled': True,
                'version': '2017-10-10'
            }
            resp = conductor.request(req_info, demands, request_parameters, service_info, template_fields,
                                     osdf_config, policies)
            if resp["plans"][0].get("recommendations"):
                placement_response = conductor_response_processor(resp, req_id, transaction_id)
            else:  # "solved" but no solutions found
                placement_response = conductor_no_solution_processor(resp, req_id, transaction_id)
            if license_info:  # Attach license solution if it exists
                placement_response['solutionInfo']['licenseInfo'] = license_info
        else:  # License selection only scenario
            placement_response = {
                "transactionId": transaction_id,
                "requestId": req_id,
                "requestStatus": "completed",
                "statusMessage": "License selection completed successfully",
                "solutionInfo": {"licenseInfo": license_info}
            }
    except Exception as err:
        error_log.error("Error for {} {}".format(req_id, traceback.format_exc()))

        try:
            body = build_json_error_body(err)
            metrics_log.info(MH.sending_response(req_id, "ERROR"))
            rc.request(json=body, noresponse=True)
        except RequestException:
            error_log.error("Error sending asynchronous notification for {} {}".format(req_id, traceback.format_exc()))
        return

    try:
        metrics_log.info(MH.calling_back_with_body(req_id, rc.url, placement_response))
        rc.request(json=placement_response, noresponse=True)
    except RequestException:  # can't do much here but log it and move on
        error_log.error("Error sending asynchronous notification for {} {}".format(req_id, traceback.format_exc()))

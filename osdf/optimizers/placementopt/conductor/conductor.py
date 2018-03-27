# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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
This application generates conductor API calls using the information received from SO and Policy platform.
"""

import json
import time

from jinja2 import Template
from requests import RequestException

from osdf.logging.osdf_logging import debug_log
from osdf.optimizers.placementopt.conductor.api_builder import conductor_api_builder
from osdf.utils.interfaces import RestClient
from osdf.operation.exceptions import BusinessException


def request(req_object, osdf_config, grouped_policies):
    """
    Process a placement request from a Client (build Conductor API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to SNIRO application (core + deployment)
    :param grouped_policies: policies related to placement (fetched based on request, and grouped by policy type)
    :param prov_status: provStatus retrieved from Subscriber policy
    :return: response from Conductor (accounting for redirects from Conductor service
    """
    config = osdf_config.deployment
    local_config = osdf_config.core
    uid, passwd = config['conductorUsername'], config['conductorPassword']
    conductor_url = config['conductorUrl']
    req_id = req_object['requestInfo']['requestId']
    transaction_id = req_object['requestInfo']['transactionId']
    headers = dict(transaction_id=transaction_id)

    max_retries = config.get('conductorMaxRetries', 30)
    ping_wait_time = config.get('conductorPingWaitTime', 60)

    rc = RestClient(userid=uid, passwd=passwd, method="GET", log_func=debug_log.debug, headers=headers)
    conductor_req_json_str = conductor_api_builder(req_object, grouped_policies, local_config)
    conductor_req_json = json.loads(conductor_req_json_str)

    debug_log.debug("Sending first Conductor request for request_id {}".format(req_id))
    resp, raw_resp = initial_request_to_conductor(rc, conductor_url, conductor_req_json)
    # Very crude way of keeping track of time.
    # We are not counting initial request time, first call back, or time for HTTP request
    total_time, ctr = 0, 2
    client_timeout = req_object['requestInfo']['timeout']
    configured_timeout = max_retries * ping_wait_time
    max_timeout = min(client_timeout, configured_timeout)

    while True:  # keep requesting conductor till we get a result or we run out of time
        if resp is not None:
            if resp["plans"][0].get("status") in ["error"]:
                raise RequestException(response=raw_resp, request=raw_resp.request)

            if resp["plans"][0].get("status") in ["done", "not found"]:
                if resp["plans"][0].get("recommendations"):
                    return conductor_response_processor(resp, raw_resp, req_id)
                else:  # "solved" but no solutions found
                    return conductor_no_solution_processor(resp, raw_resp, req_id)
            new_url = resp['plans'][0]['links'][0][0]['href']  # TODO: check why a list of lists

        if total_time >= max_timeout:
            raise BusinessException("Conductor could not provide a solution within {} seconds,"
                                    "this transaction is timing out".format(max_timeout))
        time.sleep(ping_wait_time)
        ctr += 1
        debug_log.debug("Attempt number {} url {}; prior status={}".format(ctr, new_url, resp['plans'][0]['status']))
        total_time += ping_wait_time

        try:
            raw_resp = rc.request(new_url, raw_response=True)
            resp = raw_resp.json()
        except RequestException as e:
            debug_log.debug("Conductor attempt {} for request_id {} has failed because {}".format(ctr, req_id, str(e)))


def initial_request_to_conductor(rc, conductor_url, conductor_req_json):
    """First steps in the request-redirect chain in making a call to Conductor
    :param rc: REST client object for calling conductor
    :param conductor_url: conductor's base URL to submit a placement request
    :param conductor_req_json: request json object to send to Conductor
    :return: URL to check for follow up (similar to redirects); we keep checking these till we get a result/error
    """
    debug_log.debug("Payload to Conductor: {}".format(json.dumps(conductor_req_json)))
    raw_resp = rc.request(url=conductor_url, raw_response=True, method="POST", json=conductor_req_json)
    resp = raw_resp.json()
    if resp["status"] != "template":
        raise RequestException(response=raw_resp, request=raw_resp.request)
    time.sleep(10)  # 10 seconds wait time to avoid being too quick!
    plan_url = resp["links"][0][0]["href"]
    debug_log.debug("Attemping to read the plan from the conductor provided url {}".format(plan_url))
    raw_resp = rc.request(raw_response=True, url=plan_url)  # TODO: check why a list of lists for links
    resp = raw_resp.json()

    if resp["plans"][0]["status"] in ["error"]:
        raise RequestException(response=raw_resp, request=raw_resp.request)
    return resp, raw_resp  # now the caller of this will handle further follow-ups


def conductor_response_processor(conductor_response, raw_response, req_id):
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
                "location_id": "locationId", "location_type": "locationType"}
    for reco in conductor_response['plans'][0]['recommendations']:
        for resource in reco.keys():
            c = reco[resource]['candidate']
            solution = {
                'resourceModuleName': resource,
                'serviceResourceId': reco[resource].get('service_resource_id', ""),
                'solution': {"identifier": c['inventory_type'],
                             'identifiers': [c['candidate_id']],
                             'cloudOwner': c.get('cloud_owner', "")},
                'assignmentInfo': []
            }
            for key, value in c.items():
                if key in ["location_id", "location_type", "is_rehome", "host_id"]:
                    try:
                        solution['assignmentInfo'].append({"key": name_map.get(key, key), "value": value})
                    except KeyError:
                        debug_log.debug("The key[{}] is not mapped and will not be returned in assignment info".format(key))

            for key, value in reco[resource]['attributes'].items():
                try:
                    solution['assignmentInfo'].append({"key": name_map.get(key, key), "value": value})
                except KeyError:
                    debug_log.debug("The key[{}] is not mapped and will not be returned in assignment info".format(key))
            composite_solutions.append(solution)

    request_state = conductor_response['plans'][0]['status']
    transaction_id = raw_response.headers.get('transaction_id', "")
    status_message = conductor_response.get('plans')[0].get('message', "")

    solution_info = {}
    if composite_solutions:
        solution_info.setdefault('placementSolutions', [])
        solution_info['placementSolutions'].append(composite_solutions)

    resp = {
        "transactionId": transaction_id,
        "requestId": req_id,
        "requestState": request_state,
        "statusMessage": status_message,
        "solutions": solution_info
    }
    return resp


def conductor_no_solution_processor(conductor_response, raw_response, request_id,
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
    return json.loads(templ.render(composite_solutions=[], requestId=request_id,
                                   transactionId=raw_response.headers.get('transaction_id', ""),
                                   statusMessage=status_message, json=json))



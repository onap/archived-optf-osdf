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

import json
from requests import RequestException
import time

from osdf.adapters.conductor.api_builder import conductor_api_builder
from osdf.logging.osdf_logging import debug_log
from osdf.operation.exceptions import BusinessException
from osdf.utils.interfaces import RestClient


def request(req_info, demands, request_parameters, service_info, template_fields,
            osdf_config, flat_policies):
    config = osdf_config.deployment
    local_config = osdf_config.core
    uid, passwd = config['conductorUsername'], config['conductorPassword']
    conductor_url = config['conductorUrl']
    req_id = req_info["requestId"]
    transaction_id = req_info['transactionId']
    headers = dict(transaction_id=transaction_id)
    placement_ver_enabled = config.get('placementVersioningEnabled', False)

    if placement_ver_enabled:
        cond_minor_version = config.get('conductorMinorVersion', None)
        if cond_minor_version is not None:
            x_minor_version = str(cond_minor_version)
            headers.update({'X-MinorVersion': x_minor_version})
            debug_log.debug("Versions set in HTTP header to "
                            "conductor: X-MinorVersion: {} ".format(x_minor_version))

    max_retries = config.get('conductorMaxRetries', 30)
    ping_wait_time = config.get('conductorPingWaitTime', 60)

    rc = RestClient(userid=uid, passwd=passwd, method="GET", log_func=debug_log.debug,
                    headers=headers)
    conductor_req_json_str = conductor_api_builder(req_info, demands, request_parameters,
                                                   service_info, template_fields, flat_policies,
                                                   local_config)
    conductor_req_json = json.loads(conductor_req_json_str)

    debug_log.debug("Sending first Conductor request for request_id {}".format(req_id))

    resp, raw_resp = initial_request_to_conductor(rc, conductor_url, conductor_req_json)
    # Very crude way of keeping track of time.
    # We are not counting initial request time, first call back, or time for HTTP request
    total_time, ctr = 0, 2
    client_timeout = req_info['timeout']
    configured_timeout = max_retries * ping_wait_time
    max_timeout = min(client_timeout, configured_timeout)

    while True:  # keep requesting conductor till we get a result or we run out of time
        if resp is not None:
            if resp["plans"][0].get("status") in ["error"]:
                raise RequestException(response=raw_resp, request=raw_resp.request)

            if resp["plans"][0].get("status") in ["done", "not found"]:
                return resp
            new_url = resp['plans'][0]['links'][0][0]['href']  # TODO(krishna): check why a list of lists

        if total_time >= max_timeout:
            raise BusinessException("Conductor could not provide a solution within {} seconds,"
                                    "this transaction is timing out".format(max_timeout))
        time.sleep(ping_wait_time)
        ctr += 1
        debug_log.debug("Attempt number {} url {}; prior status={}"
                        .format(ctr, new_url, resp['plans'][0]['status']))
        total_time += ping_wait_time

        try:
            raw_resp = rc.request(new_url, raw_response=True)
            resp = raw_resp.json()
        except RequestException as e:
            debug_log.debug("Conductor attempt {} for request_id {} has failed because {}"
                            .format(ctr, req_id, str(e)))


def initial_request_to_conductor(rc, conductor_url, conductor_req_json):
    """First steps in the request-redirect chain in making a call to Conductor

    :param rc: REST client object for calling conductor
    :param conductor_url: conductor's base URL to submit a placement request
    :param conductor_req_json: request json object to send to Conductor
    :return: URL to check for follow up (similar to redirects);
             we keep checking these till we get a result/error
    """
    debug_log.debug("Payload to Conductor: {}".format(json.dumps(conductor_req_json)))
    raw_resp = rc.request(url=conductor_url, raw_response=True, method="POST",
                          json=conductor_req_json)
    resp = raw_resp.json()
    if resp["status"] != "template":
        raise RequestException(response=raw_resp, request=raw_resp.request)
    time.sleep(10)  # 10 seconds wait time to avoid being too quick!
    plan_url = resp["links"][0][0]["href"]
    debug_log.debug("Attempting to read the plan from "
                    "the conductor provided url {}".format(plan_url))
    raw_resp = rc.request(raw_response=True,
                          url=plan_url)
    resp = raw_resp.json()

    if resp["plans"][0]["status"] in ["error"]:
        raise RequestException(response=raw_resp, request=raw_resp.request)
    return resp, raw_resp  # now the caller of this will handle further follow-ups

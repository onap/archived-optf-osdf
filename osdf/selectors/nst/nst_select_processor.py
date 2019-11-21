# -------------------------------------------------------------------------
#   Copyright (c)  2019 Huawei Intellectual Property
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

import traceback

from osdf.logging.osdf_logging import metrics_log, MH, error_log
from osdf.operation.error_handling import build_json_error_body
from osdf.models.api.nstSelectionResponse import NSTSelectionResponse, NSTInfo
from osdf.operation.exceptions import BusinessException
from osdf.selectors.nsconfigdb import request_ns as nsconfig_request

"""
This application generates response to NSI Selection API calls using the information received from NSI-Handler-MS.
"""


def process_nst_selection(request_json, osdf_config, flat_policies):
    """
    Process a NSI request from a Client (build config-db, policy and  API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :param flat_policies: policies related to nsi (fetched based on request)
    :return: response from NSI Selection
    """
    try:

        req_id = request_json["requestInfo"]["requestId"]
        status, nst_selector = build_solution_list(request_json, osdf_config, flat_policies)
        nst_response = get_solutions(request_json, status, nst_selector, None)
        metrics_log.info(MH.inside_worker_thread(req_id, "validating response"))
        try:
            NSTSelectionResponse(nst_response).validate()
            metrics_log.info(MH.sending_response(req_id, "SUCCESS"))
        except Exception as err1:
            metrics_log.error(MH.sending_response(req_id, "ERROR"))
            error_msg = build_json_error_body(err1)
            raise BusinessException(error_msg)

    except Exception as err:
        error_log.error("Error for {} {}".format(req_id, traceback.format_exc()))
        error_msg = build_json_error_body(err)
        nst_response = get_solutions(request_json, "failed", "", error_msg)
        metrics_log.info(MH.sending_response(req_id, "ERROR"))

    return nst_response


def get_solutions(request_json, status, nst_selector, errormsg):
    nst_resp = NSTSelectionResponse()
    nst_resp.requestId = request_json["requestInfo"]["requestId"]
    nst_resp.transactionId = request_json['requestInfo']['transactionId']
    nst_resp.requestStatus = status
    if status == "success":
        # if nst_selector content not empty
        if nst_selector:
            nst_resp.NSTInfo = nst_selector
            nst_resp.statusMessage = ""
        else:
            nst_resp.statusMessage = "Did not find any nst solution."
        # return {
        #   "transactionId": request_json['requestInfo']['transactionId'],
        #   "requestId": request_json["requestInfo"]["requestId"],
        #   "requestStatus": status,
        #   "statusMessage": errorMessage,
        #   "NSIInfo": nsi_selector.serialize()
        # }
        return nst_resp.serialize()
    else:
        nst_resp.statusMessage = errormsg
        # return {
        #    "transactionId": request_json['requestInfo']['transactionId'],
        #    "requestId": request_json["requestInfo"]["requestId"],
        #    "requestStatus": status,
        #    "statusMessage": errorMessage,
        #}
        return nst_resp.serialize()


def build_solution_list(request_json, osdf_config, flat_policies):
    status = "success"
    req_id = request_json["requestInfo"]["requestId"]
    try:
        # return static object for testing
        # nst_selector = build_nst_selector()
        # return from remote rest call
        nst_selector = nsconfig_request(request_json, osdf_config, flat_policies, 'NST')
    except RuntimeError:
        error_log.error("Failed finding solution for {} {}".format(req_id, traceback.format_exc()))
        status = "failed"
    return status, nst_selector


def build_nst_selector():
    nstselector = NSTInfo()
    nstselector.invariantUUID = "23edd22b-a0b2-449f-be87-d094159b9269"
    nstselector.UUID = "46da8cf8-0878-48ac-bea3-f2200959411a"
    nstselector.NSTName = "eMBB service"
    return nstselector

    #return {
    #    "invariantUUID":"23edd22b-a0b2-449f-be87-d094159b9269",
    #    "UUID":"46da8cf8-0878-48ac-bea3-f2200959411a",
    #    "NSIID":"61c4aa7c-9ca6-46cd-b3f8-009769db8641",
    #    "NSIName":"eMBB service"
    #}

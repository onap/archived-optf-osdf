# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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
from requests import RequestException

from osdf.logging.osdf_logging import metrics_log, MH, error_log
from osdf.operation.error_handling import build_json_error_body
from osdf.utils.interfaces import get_rest_client
from .configdb import request as config_request
from .solver.optimizer import pci_optimize as optimize
from .solver.pci_utils import get_cell_id, get_pci_value

"""
This application generates PCI Optimization API calls using the information received from PCI-Handler-MS, SDN-C
and Policy.
"""


def process_pci_optimation(request_json, osdf_config, flat_policies):
    """
    Process a PCI request from a Client (build config-db, policy and  API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :param flat_policies: policies related to pci (fetched based on request)
    :return: response from PCI Opt
    """
    try:
        rc = get_rest_client(request_json, service="pcih")
        req_id = request_json["requestInfo"]["requestId"]
        cell_info_list, network_cell_info = config_request(request_json, osdf_config, flat_policies)

        pci_response = get_solutions(cell_info_list, network_cell_info, request_json)

        metrics_log.info(MH.inside_worker_thread(req_id))
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
        metrics_log.info(MH.calling_back_with_body(req_id, rc.url, pci_response))
        rc.request(json=pci_response, noresponse=True)
    except RequestException:  # can't do much here but log it and move on
        error_log.error("Error sending asynchronous notification for {} {}".format(req_id, traceback.format_exc()))


def get_solutions(cell_info_list, network_cell_info, request_json):
    return {
        "transactionId": request_json['requestInfo']['transactionId'],
        "requestId": request_json["requestInfo"]["requestId"],
        "requestStatus": "completed",
        "statusMessage": "success",
        "solutions": [
            {
                'networkId': request_json['cellInfo']['networkId'],
                'pciSolutions': build_solution_list(cell_info_list, network_cell_info, request_json)
            }
        ]
    }


def build_solution_list(cell_info_list, network_cell_info, request_json):
    solution_list = []
    for cell in request_json['cellInfo']['cellIdList']:
        opt_solution = optimize(cell, network_cell_info, cell_info_list)
        sol = opt_solution[0]['pci']
        for k, v in sol.items():
            response = {
                'cellId': get_cell_id(network_cell_info, k),
                'pci': get_pci_value(network_cell_info, v)
            }
            solution_list.append(response)
    return solution_list

# -------------------------------------------------------------------------
#    Copyright (C) 2020 Wipro Limited.
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
from osdf.logging.osdf_logging import metrics_log, MH, error_log, audit_log
from apps.placement.optimizers.conductor import conductor
from osdf.utils.mdc_utils import mdc_from_json


def process_nsi_selection(request_json, policies, osdf_config):
    """Perform the work for placement optimization (e.g. call SDC artifact and make conductor request)
    NOTE: there is scope to make the requests to policy asynchronous to speed up overall performance
    :param request_json: json content from original request
    :param policies: flattened policies corresponding to this request
    :param osdf_config: configuration specific to OSDF app
    :return: response which has to be sent to so
    """

    try:
        mdc_from_json(request_json)
        req_id = request_json["requestInfo"]["requestId"]
        transaction_id = request_json['requestInfo']['transactionId']
        test = True
        if test: # to-do add a condition here
            metrics_log.info(MH.requesting("placement/conductor", req_id))
            for nst in request_json["NSTInfo"]:
                audit_log.info("for every nst")
                audit_log.info(nst)
                mod_request_json = form_req_json(request_json, nst)
                placement_response = conductor.request(mod_request_json, osdf_config, policies, "slice")
        return placement_response
    except Exception as err:
        error_log.error("Error for {} {}".format(req_id, traceback.format_exc()))


def form_req_json(request_json, nst):
    try:
        # request_json["resourceModelInfo"] = request_json.pop("NSTInfo")
        #request_json.pop("NSTInfo")
        request_json["NSTInfo"] = nst
        audit_log.info("new request")
        audit_log.info(request_json)
        return request_json
    except Exception as err:
        error_log.error("Error while forming nst request")
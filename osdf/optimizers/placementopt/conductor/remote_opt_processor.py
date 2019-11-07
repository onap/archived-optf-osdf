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

from requests import RequestException

import traceback
from osdf.operation.error_handling import build_json_error_body
from osdf.logging.osdf_logging import metrics_log, MH, error_log
from osdf.optimizers.placementopt.conductor import conductor
from osdf.optimizers.licenseopt.simple_license_allocation import license_optim
from osdf.utils.interfaces import get_rest_client
from osdf.utils.mdc_utils import mdc_from_json


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
            placement_response = conductor.request(request_json, osdf_config, policies)
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
        metrics_log.info(MH.calling_back_with_body(req_id, rc.url,placement_response))
        rc.request(json=placement_response, noresponse=True)
    except RequestException :  # can't do much here but log it and move on
        error_log.error("Error sending asynchronous notification for {} {}".format(req_id, traceback.format_exc()))


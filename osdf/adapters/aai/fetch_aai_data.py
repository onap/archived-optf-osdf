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

import json
import requests
from requests.auth import HTTPBasicAuth
from requests import RequestException

from osdf.logging.osdf_logging import debug_log

AAI_HEADERS = {
    "X-TransactionId": "9999",
    "X-FromAppId": "OOF",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

AUTH = HTTPBasicAuth("AAI", "AAI")


class AAIException(Exception):
    pass


def get_aai_data(request_json, osdf_config):

    """Get the response from AAI

       :param request_json: requestjson
       :param osdf_config: configuration specific to OSDF app
       :return:response body from AAI
    """

    nxi_id = request_json["NxIId"]
    config = osdf_config.deployment
    aai_url = config["aaiUrl"]
    aai_req_url = aai_url + config["aaiServiceInstanceUrl"] + nxi_id + "?depth=2"

    try:
        response = requests.get(aai_req_url, headers=AAI_HEADERS, auth=AUTH, verify=False)
    except RequestException as e:
        raise AAIException("Request exception was encountered {}".format(e))

    if response.status_code == 200:
        return response.json()
    else:
        raise AAIException("Error response recieved from AAI for the request {}".format(aai_req_url))


def execute_dsl_query(query, format, osdf_config):
    """Get the response from AAI

           :param query: dsl query to be executed
           :param format format of the output
           :param osdf_config: configuration specific to OSDF app
           :return:response body from AAI
    """
    config = osdf_config.deployment
    dsl_url = config["aaiUrl"] + config["dslQueryPath"] + format

    data = json.dumps({'dsl': query})
    debug_log.debug("aai dsl request: {}".format(data))
    try:
        response = requests.put(dsl_url, data=data, headers=AAI_HEADERS, auth=AUTH, verify=False)
    except RequestException as ex:
        raise AAIException("Request exception was encountered {}".format(ex))

    if response.status_code == 200:
        return response.json()
    else:
        raise AAIException("Response code other than 200 from AAI: {} {}".format(response.status_code,
                                                                                 response.content))

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

import requests
from requests.exceptions import HTTPError

from osdf.config.base import osdf_config
from osdf.utils.interfaces import RestClient


class DESException(Exception):
    pass


def extract_data(service_id, request_data):
    """Extracts data from the data lake via DES.

    param: service_id: kpi data identifier
    param: request_data: data to send
    param: osdf_config: osdf config to retrieve api info
    """

    config = osdf_config.deployment
    user, password = config['desUsername'], config['desPassword']
    headers = config["desHeaders"]
    req_url = config["desUrl"] + config["desApiPath"] + service_id
    rc = RestClient(userid=user, passwd=password, url=req_url, headers=headers, method="POST")

    try:
        response_json = rc.request(data=request_data)
        return response_json.get("result")
    except requests.RequestException as e:
        raise DESException("Request exception was encountered {}".format(e))
    except HTTPError as ex:
        raise DESException("Response code other than 200. Response code: {}".format(ex.response.status_code))

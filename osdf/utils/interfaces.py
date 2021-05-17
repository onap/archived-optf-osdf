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

import json
import requests
import yaml

from osdf.config.base import creds_prefixes
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import MH


def get_rest_client(request_json, service):
    """Get a RestClient based on request_json's callback URL and osdf_config's credentials based on service name

    :param request_json:
    :param service: so or cm
    :return: rc -- RestClient
    """
    callback_url = request_json["requestInfo"]["callbackUrl"]
    prefix = creds_prefixes[service]
    config = osdf_config.deployment
    c_userid, c_passwd = config[prefix + "Username"], config[prefix + "Password"]
    return RestClient(url=callback_url, userid=c_userid, passwd=c_passwd)


def json_from_file(file_name):
    """Read a policy from a file"""
    with open(file_name) as fid:
        return json.load(fid)


def yaml_from_file(file_name):
    """Read a policy from a file"""
    with open(file_name) as fid:
        return yaml.load(fid)


class RestClient(object):
    """Simple REST Client that supports get/post and basic auth"""

    def __init__(self, userid=None, passwd=None, log_func=None, url=None, timeout=None, headers=None,
                 method="POST", req_id=None, verify=None):
        self.auth = (userid, passwd) if userid and passwd else None
        self.headers = headers if headers else {}
        self.method = method
        self.url = url
        self.log_func = log_func
        self.timeout = (30, 90) if timeout is None else timeout
        self.req_id = req_id
        self.verify = verify

    def add_headers(self, headers):
        self.headers.update(headers)

    def request(self, url=None, method=None, asjson=True, ok_codes=(2, ),
                raw_response=False, noresponse=False, timeout=None, **kwargs):
        """Sends http request to the specified url

        :param url: REST end point to query
        :param method: GET or POST (default is None => self.method)
        :param asjson: whether the expected response is in json format
        :param ok_codes: expected codes (prefix matching -- e.g. can be (20, 21, 32) or (2, 3))
        :param noresponse: If no response is expected (as long as response codes are OK)
        :param raw_response: If we need just the raw response (e.g. conductor sends transaction IDs in headers)
        :param timeout: Connection and read timeouts
        :param kwargs: Other parameters
        :return:
        """
        if not self.req_id:
            debug_log.debug("Requesting URL: {}".format(url or self.url))
        else:
            debug_log.debug("Requesting URL: {} for request ID: {}".format(url or self.url, self.req_id))

        if not url:
            url = self.url
        if not self.verify and url.startswith("https"):
            verify = osdf_config.deployment["aaf_ca_certs"]
        else:
            verify = self.verify

        res = requests.request(url=url or self.url, method=method or self.method,
                               auth=self.auth, headers=self.headers,
                               timeout=timeout or self.timeout, verify=verify, **kwargs)

        if self.log_func:
            self.log_func(MH.received_http_response(res))

        res_code = str(res.status_code)
        if not any(res_code.startswith(x) for x in map(str, ok_codes)):
            raise BaseException(res.raise_for_status())

        if raw_response:
            return res
        elif noresponse:
            return None
        elif asjson:
            return res.json()
        else:
            return res.content

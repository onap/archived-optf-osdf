# -------------------------------------------------------------------------
#   Copyright (c) 2017-2018 AT&T Intellectual Property
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
import unittest

from requests.models import Response
from osdf.utils.interfaces import RestClient, get_rest_client
from unittest.mock import patch


m1 = Response()
m1._content = b'{"msg": "OK"}'
m1.status_code = 202
mock_good_response = m1

m2 = Response()
m2._content = b'{"msg": "Not-OK"}'
m2.status_code = 403
mock_bad_response = m2


class TestOsdfUtilsInterfaces(unittest.TestCase):
    @patch('requests.request', return_value=mock_good_response)
    def test_rc_request(self, mock_good_response):
        rc = RestClient()
        rc.add_headers({})
        rc.request(url="http://localhost", req_id="testReq")

    @patch('requests.request', return_value=mock_good_response)
    def test_rc_request_v1(self, mock_good_response):
        rc = RestClient()
        rc.add_headers({})
        rc.request(url="http://localhost", asjson=False, log_func=lambda x: None)
        rc.request(url="http://localhost", raw_response=True)
        rc.request(url="http://localhost", no_response=True)

    @patch('requests.request', return_value=mock_bad_response)
    def test_rc_request_v2(self, mock_bad_response):
        rc = RestClient()
        try:
            rc.request(url="http://localhost")
        except requests.RequestException:
            return
        raise Exception("Allows bad requests instead of raising exception")

    def test_get_rest_client(self):
        request_json = {"requestInfo": {"callbackUrl": "http://localhost"}}
        service = "so"
        get_rest_client(request_json, service)


if __name__ == "__main__":
    unittest.main()


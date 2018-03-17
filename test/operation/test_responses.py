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
import unittest
import json
import yaml

from osdf.adapters.local_data import local_policies


class TestLocalPolicies(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.folder = './test/policy-local-files'
        self.invalid_policies = ['INVALID-one.json', 'INVALID-two.json']
        self.valid_policies = [
            'Affinity_vCPE_1.json',
            'Capacity_vG_1.json',
            'Distance_vG_1.json',
            'Placement_Optimization_1.json',
            'hpa_policy_vGMuxInfra_1.json',
            'vnfPolicy_vG.json',
            'Capacity_vGMuxInfra.json',
            'Distance_vGMuxInfra_1.json',
            'Min_Guarantee_vGMuxInfra_1.json',
            'QueryPolicy_vCPE.json',
            'hpa_policy_vG_1.json',
            'vnfPolicy_vGMuxInfra.json'
            ]
       
    def test_get_local_policies_no_policies(self):
        with self.assertRaises(FileNotFoundError):
             res = local_policies.get_local_policies(self.folder, self.invalid_policies)
             assert res is None

    def test_get_local_valid_policies(self):
        res = local_policies.get_local_policies(self.folder, self.valid_policies)
        assert len(res) == len(self.valid_policies)

    def test_get_subset_valid_policies(self):
        wanted = [ x[:-5] for x in self.valid_policies[:1] ]
        res = local_policies.get_local_policies(self.folder, self.valid_policies, wanted)
        assert len(res) == len(wanted)


if __name__ == "__main__":
    unittest.main()

from flask import Response

from osdf import ACCEPTED_MESSAGE_TEMPLATE


def osdf_response_for_request_accept(req_id="", text="", response_code=202, as_http=True):
    """Helper method to create a response object for request acceptance, so that the object can be sent to a client
    :param req_id: request ID provided by the caller
    :param text: extra text description about accepting the request (e.g. "Request accepted")
    :param response_code: the HTTP status code to send -- default is 202 (accepted)
    :param as_http: whether to send response as HTTP response object or as a string
    :return: if as_http is True, return a HTTP Response object. Otherwise, return json-encoded-message
    """
    response_message = ACCEPTED_MESSAGE_TEMPLATE.render(description=text, request_id=req_id)
    if not as_http:
        return response_message

    response = Response(response_message, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(response_message))
    response.status_code = response_code
    return response

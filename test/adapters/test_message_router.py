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
import osdf.adapters.dcae.message_router as MR
import unittest

from osdf.operation.exceptions import MessageBusConfigurationException
from unittest.mock import patch


class TestMessageRouter(unittest.TestCase):

    def test_valid_MR(self):
        mr = MR.MessageRouterClient(dmaap_url="https://MYHOST:3905")

    def test_valid_MR_with_base_urls(self):
        base_urls = ["https://MYHOST1:3905/events/MY-TOPIC","https://MYHOST2:3905/events/MY-TOPIC"]
        mr = MR.MessageRouterClient(dmaap_url=base_urls)

    def test_invalid_valid_MR_with_base_urls(self):
        """No dmaap_url"""
        try:
            mr = MR.MessageRouterClient()
        except MessageBusConfigurationException:
            return

        raise Exception("Allows invalid MR configuration") # if it failed to error out

    @patch('osdf.adapters.dcae.message_router.MessageRouterClient.http_request', return_value={})
    def test_mr_http_request_mocked(self, http_request):
        mr = MR.MessageRouterClient(dmaap_url="https://MYHOST:3905")
        mr.http_request = http_request
        assert mr.get() == {} 
        assert mr.post("Hello") == {} 

    def test_mr_http_request_non_existent_host(self):
        mr = MR.MessageRouterClient(dmaap_url="https://MYHOST:3905")
        try:
            mr.get()
        except:
            return

        raise Exception("Allows invalid host") # if it failed to error out
if __name__ == "__main__":
    unittest.main()


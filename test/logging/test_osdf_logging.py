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

from osdf.logging import osdf_logging as L1
from osdf.logging.osdf_logging import OOFOSDFLogMessageHelper as MH
from osdf.logging.osdf_logging import OOFOSDFLogMessageFormatter as formatter
from unittest import mock


class TestOSDFLogging(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.MH = MH()
        self.err = Exception("Some Exception")
        self.req_id = "TEST-Req-ID"
        self.url = mock.MagicMock()
        self.request = mock.MagicMock()
        self.client = mock.MagicMock()
        self.service_name = mock.MagicMock()
        self.callback_url = mock.MagicMock()
        self.service_name = mock.MagicMock()
        self.body = mock.MagicMock()
        self.desc = mock.MagicMock()
        self.response = mock.MagicMock()
        self.remote_addr = mock.MagicMock()
        self.json_body = mock.MagicMock()
        self.F = formatter

    def test_format_exception(self):
        res = L1.format_exception(Exception("Some error"))

    def test_accepted_valid_request(self):
        res = formatter.accepted_valid_request(self.req_id, self.request)
        assert res.startswith("Accepted valid request")

    def test_invalid_request(self):
        res = formatter.invalid_request(self.req_id, self.err)
        assert res.startswith("Invalid request")

    def test_invalid_response(self):
        res = formatter.invalid_response(self.req_id, self.err)
        assert res.startswith("Invalid response")

    def test_malformed_request(self):
        res = formatter.malformed_request(self.request, self.err)
        assert res.startswith("Malformed request")

    def test_malformed_response(self):
        res = formatter.malformed_response(self.response, self.client, self.err)
        assert res.startswith("Malformed response")

    def test_need_policies(self):
        res = formatter.need_policies(self.req_id)
        assert res.startswith("Policies required but")

    def test_policy_service_error(self):
        res = formatter.policy_service_error(self.url, self.req_id, self.err)
        assert res.startswith("Unable to call policy")

    def test_requesting_url(self):
        res = formatter.requesting_url(self.url, self.req_id)
        assert res.startswith("Making a call to URL")

    def test_requesting(self):
        res = formatter.requesting(self.service_name, self.req_id)
        assert res.startswith("Making a call to service")

    def test_error_requesting(self):
        res = formatter.error_requesting(self.service_name, self.req_id, self.err)
        assert res.startswith("Error while requesting service")

    def test_error_calling_back(self):
        res = formatter.error_calling_back(self.service_name, self.callback_url, self.err)
        assert res.startswith("Error while posting result to callback URL")
        
    def test_calling_back(self):
        res = formatter.calling_back(self.req_id, self.callback_url)
        assert res.startswith("Posting result to callback URL")

    def test_calling_back_with_body(self):
        res = formatter.calling_back_with_body(self.req_id, self.callback_url, self.body)
        assert res.startswith("Posting result to callback URL")

    def test_received_request(self):
        res = formatter.received_request(self.url, self.remote_addr, self.json_body)
        assert res.startswith("Received a call")

    def test_new_worker_thread(self):
        res = formatter.new_worker_thread(self.req_id)
        assert res.startswith("Initiating new worker thread")

    def test_inside_worker_thread(self):
        res = formatter.inside_worker_thread(self.req_id)
        assert res.startswith("Inside worker thread for request ID")

    def test_inside_new_thread(self):
        res = formatter.inside_new_thread(self.req_id)
        assert res.startswith("Spinning up a new thread for request ID")

    def test_processing(self):
        res = formatter.processing(self.req_id, self.desc)
        assert res.startswith("Processing request ID")

    def test_processed(self):
        res = formatter.processed(self.req_id, self.desc)
        assert res.startswith("Processed request ID")

    def test_error_while_processing(self):
        res = formatter.error_while_processing(self.req_id, self.desc, self.err)
        assert res.startswith("Error while processing request ID")

    def test_creating_local_env(self):
        res = formatter.creating_local_env(self.req_id)
        assert res.startswith("Creating local environment request ID")

    def test_error_local_env(self):
        res = formatter.error_local_env(self.req_id, self.desc, self.err)
        assert res.startswith("Error while creating local environment for request ID")

    def test_error_response_posting(self):
        res = formatter.error_response_posting(self.req_id, self.desc, self.err)
        assert res.startswith("Error while posting a response for a request ID")

    def test_received_http_response(self):
        res = formatter.received_http_response(self.response)
        assert res.startswith("Received response [code: ")

    def test_sending_response(self):
        res = formatter.sending_response(self.req_id, self.desc)
        assert res.startswith("Response is sent for request ID")

    def test_listening_response(self):
        res = formatter.listening_response(self.req_id, self.desc)
        assert res.startswith("Response is sent for request ID")

    def test_items_received(self):
        res = formatter.items_received(10, "messages")
        assert res == "Received 10 messages"

    def test_items_sent(self):
        res = formatter.items_sent(10, "messages")
        assert res == "Published 10 messages"

    def test_warn_audit_error(self):
        """Log the message to error_log.warn and audit_log.warn"""
        L1.warn_audit_error("Some warning message")


if __name__ == "__main__":
    unittest.main()


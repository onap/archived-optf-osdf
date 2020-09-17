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
from unittest import TestCase
from unittest import mock
from unittest.mock import patch

from requests import Request
from requests import RequestException
from schematics.exceptions import DataError

from osdf.apps import baseapp
from osdf.apps.baseapp import app
from osdf.operation.exceptions import BusinessException


class TestOSDFApp(TestCase):

    def setUp(self):
        with app.app_context():
            self.patcher_g = patch('osdf.apps.baseapp.g', return_value={'request_id': 'DUMMY-REQ'})
            self.Mock_g = self.patcher_g.start()
        # self.patcher2 = patch('package.module.Class2')
        # self.MockClass2 = self.patcher2.start()

    def tearDown(self):
        patch.stopall()

    def dummy_request_exception(self):
        e = RequestException("Web Request Exception Description")
        e.response = mock.MagicMock()
        e.request = Request(method="GET", url="SOME-URL")
        e.response.status_code = 400
        e.response.content = "Some request exception occurred"
        # request().raise_for_status.side_effect = e
        return e

    def test_handle_business_exception(self):
        e = BusinessException("Business Exception Description")
        resp = baseapp.handle_business_exception(e)
        assert resp.status_code == 400

    def test_handle_request_exception(self):
        e = self.dummy_request_exception()
        resp = baseapp.handle_request_exception(e)
        assert resp.status_code == 400

    def test_handle_data_error(self):
        e = DataError({"A1": "A1 Data Error"})
        resp = baseapp.handle_data_error(e)
        assert resp.status_code == 400

    def test_internal_failure(self):
        e = Exception("An Internal Error")
        resp = baseapp.internal_failure(e)
        assert resp.status_code == 500

    def test_get_options_default(self):
        baseapp.get_options(["PROG"])  # ensure nothing breaks


if __name__ == "__main__":
    unittest.main()

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

import mock
from mock import patch
from requests import RequestException
from requests.exceptions import HTTPError
import unittest
from osdf.adapters.dcae import des
from osdf.adapters.dcae.des import DESException
import osdf.config.loader as config_loader
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict


class TestDes(unittest.TestCase):

    def setUp(self):
        self.config_spec = {
            "deployment": "config/osdf_config.yaml",
            "core": "config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

    def tearDown(self):
        pass

    def test_extract_data(self):
        response_file = 'test/adapters/dcae/des_response.json'
        response_json = json_from_file(response_file)

        des_config = self.osdf_config.core['PCI']['DES']
        service_id = des_config['service_id']
        data = des_config['filter']
        expected = response_json['result']
        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = response_json
        self.patcher_req = patch('requests.request', return_value=response)
        self.Mock_req = self.patcher_req.start()
        self.assertEqual(expected, des.extract_data(service_id, data))
        self.patcher_req.stop()

        response = mock.MagicMock()
        response.status_code = 404
        response.raise_for_status.side_effect = HTTPError("404")
        self.patcher_req = patch('requests.request', return_value=response)
        self.Mock_req = self.patcher_req.start()
        self.assertRaises(DESException, des.extract_data, service_id, data)
        self.patcher_req.stop()

        self.patcher_req = patch('requests.request', side_effect=RequestException("error"))
        self.Mock_req = self.patcher_req.start()
        self.assertRaises(DESException, des.extract_data, service_id, data)
        self.patcher_req.stop()

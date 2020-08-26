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

import unittest
import mock
from unittest.mock import patch
from osdf.config.base import osdf_config
import osdf.config.loader as config_loader
from osdf.utils.programming_utils import DotDict
from osdf.utils.interfaces import json_from_file
from osdf.adapters.aai.fetch_aai_data import get_aai_data,AAIException

class TestRemoteOptProcessor(unittest.TestCase):
    def setUp(self):
        self.config_spec = {
            "deployment": "config/osdf_config.yaml",
            "core": "config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

    def tearDown(self):

        patch.stopall()


    def test_get_aai_data(self):
        main_dir = ""
        response_file = main_dir + 'test/apps/nxi_termination/aai_response.json'
        exception_response_file = main_dir + 'test/apps/nxi_termination/aai_exception_response.json'
        request_file = main_dir + 'test/apps/nxi_termination/nxi_termination.json'
        response_json = json_from_file(response_file)
        request_json = json_from_file(request_file)
        exception_json = json_from_file(exception_response_file)
        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = response_json
        self.patcher_req = patch('requests.get',
                                         return_value = response)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(response_json, get_aai_data(request_json,osdf_config))
        self.patcher_req.stop()

        responsenew=mock.MagicMock()
        responsenew.status_code=404
        responsenew.json.return_value = exception_json
        self.patcher_req = patch('requests.get',
                                 return_value=responsenew)
        self.Mock_req = self.patcher_req.start()
        self.assertRaises( AAIException,get_aai_data,request_json,osdf_config)
        self.patcher_req.stop()


if __name__ == "__main__":
    unittest.main()
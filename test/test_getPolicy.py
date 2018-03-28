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
import json
import unittest

from osdf.adapters.policy.interface import get_policies
from osdf.utils.interfaces import json_from_file
from mock import patch


class TestGetPolicy(unittest.TestCase):

    def setUp(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/placement-tests/request.json"   # "test/placement-tests/request.json"
        self.request_json = json_from_file(parameter_data_file)

    def test_get_policy_function(self):
        with patch('osdf.adapters.policy.interface.remote_api', return_value=[{"x: y"}]):
            policy_list = get_policies(self.request_json, "placement")
            policy_exist = True if len(policy_list) > 0 else False
            self.assertEqual(policy_exist, True)

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
import os
import unittest

import mock

import osdf.config.loader as config_loader
from osdf.adapters.local_data import local_policies
from osdf.adapters.policy import interface as pol
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict


class TestPolicyInterface(unittest.TestCase):

    def setUp(self):
        self.config_spec = {
            "deployment": os.environ.get("OSDF_MANAGER_CONFIG_FILE", "config/osdf_config.yaml"),
            "core": "config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

        main_dir = ""
        conductor_api_template = main_dir + "osdf/templates/conductor_interface.json"
        parameter_data_file = main_dir + "test/placement-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        self.valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        self.request_json = json_from_file(parameter_data_file)
        self.policies = [json_from_file(policy_data_path + '/' + name) for name in self.valid_policies_files]

    def tearDown(self):
        pass

    def test_get_by_name(self):
        pol.get_by_name(mock.MagicMock(), self.valid_policies_files[0])


if __name__ == "__main__":
    unittest.main()


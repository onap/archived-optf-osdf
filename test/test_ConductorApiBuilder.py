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
from osdf.optimizers.placementopt.conductor.api_builder import conductor_api_builder
from osdf.utils.interfaces import json_from_file


class TestConductorApiBuilder(unittest.TestCase):

    def setUp(self):
        self.main_dir = ""
        conductor_api_template = self.main_dir + "osdf/templates/conductor_interface.json"
        parameter_data_file = self.main_dir + "test/placement-tests/request.json"    # "test/placement-tests/request.json"
        policy_data_path = self.main_dir + "test/policy-local-files"                 # "test/policy-local-files"
        local_config_file = self.main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        self.request_json = json_from_file(parameter_data_file)
        self.policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]


    def test_conductor_api_call_builder(self):
        main_dir = self.main_dir
        conductor_api_template = main_dir + "osdf/templates/conductor_interface.json" # "osdf/templates/conductor_interface.json"
        local_config_file = main_dir + "config/common_config.yaml"
        request_json = self.request_json
        policies = self.policies
        local_config = yaml.load(open(local_config_file))
        templ_string = conductor_api_builder(request_json, policies, local_config, conductor_api_template)
        templ_json = json.loads(templ_string)
        self.assertEqual(templ_json["name"], "yyy-yyy-yyyy")


if __name__ == "__main__":
    unittest.main()


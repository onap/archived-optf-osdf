# -------------------------------------------------------------------------
#   Copyright (c) 2017-2018 AT&T Intellectual Property
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
import json
import yaml

from osdf.adapters.conductor.api_builder import conductor_api_builder
from osdf.adapters.local_data import local_policies
from osdf.utils.interfaces import json_from_file


class TestConductorApiBuilder(unittest.TestCase):

    def setUp(self):
        self.main_dir = ""
        self.conductor_api_template = self.main_dir + "osdf/adapters/conductor/templates/conductor_interface.json"
        self.local_config_file = self.main_dir + "config/common_config.yaml"
        policy_data_path = self.main_dir + "test/policy-local-files"                 # "test/policy-local-files"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        parameter_data_file = self.main_dir + "test/placement-tests/request.json"    # "test/placement-tests/request.json"
        self.request_json = json_from_file(parameter_data_file)
        parameter_data_file = self.main_dir + "test/placement-tests/request_vfmod.json"
        self.request_vfmod_json = json_from_file(parameter_data_file)
        parameter_data_file = self.main_dir + "test/placement-tests/request_placement_vfmod.json"
        self.request_placement_vfmod_json = json_from_file(parameter_data_file)
        self.policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]
        self.template_fields = {
            'location_enabled': True,
            'version': '2017-10-10'
        }

    def test_conductor_api_call_builder(self):
        main_dir = self.main_dir
        request_json = self.request_json
        policies = self.policies
        local_config = yaml.safe_load(open(self.local_config_file))
        req_info = request_json['requestInfo']
        demands = request_json['placementInfo']['placementDemands']
        request_parameters = request_json['placementInfo']['requestParameters']
        service_info = request_json['serviceInfo']
        templ_string = conductor_api_builder(req_info, demands, request_parameters, service_info, self.template_fields,
                                             policies, local_config, self.conductor_api_template)
        templ_json = json.loads(templ_string)
        self.assertEqual(templ_json["name"], "yyy-yyy-yyyy")

    def test_conductor_api_call_builder_vfmod(self):
        request_json = self.request_vfmod_json
        policies = self.policies
        local_config = yaml.safe_load(open(self.local_config_file))
        req_info = request_json['requestInfo']
        demands = request_json['placementInfo']['placementDemands']
        request_parameters = request_json['placementInfo']['requestParameters']
        service_info = request_json['serviceInfo']
        templ_string = conductor_api_builder(req_info, demands, request_parameters, service_info, self.template_fields,
                                             policies, local_config, self.conductor_api_template)
        templ_json = json.loads(templ_string)
        self.assertEqual(templ_json, self.request_placement_vfmod_json)


if __name__ == "__main__":
    unittest.main()


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

from osdf.adapters.local_data import local_policies
from osdf.adapters.conductor import translation as tr
from osdf.utils.interfaces import json_from_file


class TestConductorTranslation(unittest.TestCase):

    def setUp(self):
        self.main_dir = ""
        self.conductor_api_template = self.main_dir + "osdf/templates/conductor_interface.json"
        self.local_config_file = self.main_dir + "config/common_config.yaml"
        policy_data_path = self.main_dir + "test/policy-local-files"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        parameter_data_file = self.main_dir + "test/placement-tests/request.json"
        self.request_json = json_from_file(parameter_data_file)
        parameter_data_file = self.main_dir + "test/placement-tests/request_vfmod.json"
        self.request_vfmod_json = json_from_file(parameter_data_file)
        self.policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]

        self.optimization_policies = [json_from_file(policy_data_path + '/' + "NSI_optimization.json")]

    def tearDown(self):
        pass

    def test_gen_demands(self):
        # need to run this only on vnf policies
        vnf_policies = [x for x in self.policies if x[list(x.keys())[0]]["type"]
                        == "onap.policies.optimization.VnfPolicy"]
        res = tr.gen_demands(self.request_json['placementInfo']['placementDemands'], vnf_policies)

        assert res is not None

    def test_gen_vfmod_demands(self):
        # need to run this only on vnf policies
        vnf_policies = [x for x in self.policies if x[list(x.keys())[0]]["type"]
                        == "onap.policies.optimization.VnfPolicy"]
        res = tr.gen_demands(self.request_vfmod_json['placementInfo']['placementDemands'], vnf_policies)
        assert res is not None

    def test_gen_optimization_policy(self):
        expected = [{
            "goal": "minimize",
            "operation_function": {
                "operator": "sum",
                "operands": [
                    {
                        "function": "attribute",
                        "params": {
                            "attribute": "creation_cost",
                            "demand": "URLLC"
                        }
                    }
                ]
            }
        }]
        self.assertEqual(expected,
                         tr.gen_optimization_policy(self.request_vfmod_json['placementInfo']['placementDemands'],
                                                    self.optimization_policies))


if __name__ == "__main__":
    unittest.main()


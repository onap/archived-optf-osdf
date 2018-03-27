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
import mock
import unittest

from flask import Response
from mock import patch
from osdf.adapters.local_data import local_policies
from osdf.optimizers.placementopt.conductor import translation as tr
from osdf.utils.interfaces import json_from_file, yaml_from_file


class TestConductorTranslation(unittest.TestCase):

    def setUp(self):
        main_dir = ""
        conductor_api_template = main_dir + "osdf/templates/conductor_interface.json"
        parameter_data_file = main_dir + "test/placement-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        self.request_json = json_from_file(parameter_data_file)
        self.policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]

    def tearDown(self):
        pass

    def test_gen_demands(self):
        # need to run this only on vnf policies
        vnf_policies = [x for x in self.policies if x["content"]["policyType"] == "vnfPolicy"]
        res = tr.gen_demands(self.request_json, vnf_policies)
        assert res is not None


if __name__ == "__main__":
    unittest.main()


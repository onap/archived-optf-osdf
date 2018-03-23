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

from osdf.adapters.local_data import local_policies
from osdf.config.base import osdf_config
from osdf.adapters.policy import interface
from osdf.utils.interfaces import RestClient, json_from_file
import yaml
from mock import patch
from osdf.optimizers.placementopt.conductor import translation
from osdf.operation.exceptions import BusinessException


class TestPolicyCalls(unittest.TestCase):

    def setUp(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/placement-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        self.request_json = json_from_file(parameter_data_file)
        self.policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]

    def tearDown(self):
        pass

    def test_policy_api_call(self):
        req_json_file = "./test/placement-tests/request.json"        # For tox change this to ./test/placement-tests/..
        req_json = json.loads(open(req_json_file).read())
        policy_response_file = "./test/placement-tests/policy_response.json"
        policy_response = json.loads(open(policy_response_file).read())
        with patch('osdf.adapters.policy.interface.policy_api_call', return_value=policy_response):
            policy_list = interface.remote_api(req_json, osdf_config, service_type="placement")
            self.assertIsNotNone(policy_list)

    def test_policy_api_call_failed_1(self):
        req_json_file = "./test/placement-tests/request_error1.json"        # For tox change this to ./test/placement-tests/..
        req_json = json.loads(open(req_json_file).read())
        policy_response_file = "./test/placement-tests/policy_response.json"
        policy_response = json.loads(open(policy_response_file).read())
        with patch('osdf.adapters.policy.interface.policy_api_call', return_value=policy_response):
            self.assertRaises(BusinessException,
                              lambda: interface.remote_api(req_json, osdf_config, service_type="placement"))

    def test_policy_api_call_failed_2(self):
        req_json_file = "./test/placement-tests/request.json"        # For tox change this to ./test/placement-tests/..
        req_json = json.loads(open(req_json_file).read())
        policy_response_file = "./test/placement-tests/policy_response_error1.json"
        policy_response = json.loads(open(policy_response_file).read())
        with patch('osdf.adapters.policy.interface.policy_api_call', return_value=policy_response):
            self.assertRaises(BusinessException,
                              lambda: interface.remote_api(req_json, osdf_config, service_type="placement"))

    def test_policy_api_call_failed_3(self):
        req_json_file = "./test/placement-tests/request.json"        # For tox change this to ./test/placement-tests/..
        req_json = json.loads(open(req_json_file).read())
        policy_response_file = "./test/placement-tests/policy_response_error2.json"
        policy_response = json.loads(open(policy_response_file).read())
        with patch('osdf.adapters.policy.interface.policy_api_call', return_value=policy_response):
            self.assertRaises(BusinessException,
                              lambda: interface.remote_api(req_json, osdf_config, service_type="placement"))
    
    def test_get_by_scope(self):
        req_json_file = "./test/placement-tests/testScoperequest.json"
        all_policies = "./test/placement-tests/policy_response.json"
        req_json_obj = json.loads(open(req_json_file).read())
        req_json_obj2 = json.loads(open(all_policies).read())
        yaml_file = "./test/placement-tests/test_by_scope.yaml"

        with open(yaml_file) as yaml_file2:
            policy_config_file = yaml.load(yaml_file2)
            with patch('osdf.utils.interfaces.RestClient.request', return_value=req_json_obj2):
                policies_list = interface.get_by_scope(RestClient, req_json_obj, policy_config_file, 'placement')
                self.assertTrue(policies_list, 'is null')
                self.assertRaises(Exception)

    def test_gen_demands(self):
        actionsList = []
        genDemandslist = []
        req_json = "./test/placement-tests/request.json"
        req_json = json.loads(open(req_json).read())
        genDemands = translation.gen_demands(req_json, self.policies)
        for action in req_json['placementInfo']['placementDemands']:
            actionsList.append(action['resourceModuleName'])
        for key2,value in genDemands.items():
            genDemandslist.append(key2)
        self.assertListEqual(genDemandslist, actionsList, 'generated demands are not equal to the passed input'
                                                          '[placementDemand][resourceModuleName] list')
           
if __name__ == '__main__':
    unittest.main()

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

from apps.placement.optimizers.conductor.remote_opt_processor import process_placement_opt
from osdf.adapters.local_data import local_policies
from osdf.utils.interfaces import json_from_file, yaml_from_file


class TestProcessPlacementOpt(unittest.TestCase):

    def setUp(self):
        mock_req_accept_message = Response("Accepted Request", content_type='application/json; charset=utf-8')
        conductor_response_file = 'test/placement-tests/conductor_response.json'
        conductor_response = json_from_file(conductor_response_file)
        self.patcher_req = patch('osdf.adapters.conductor.conductor.request',
                                 return_value=conductor_response)
        self.patcher_req_accept = patch('osdf.operation.responses.osdf_response_for_request_accept',
                                        return_value=mock_req_accept_message)
        self.patcher_callback = patch(
            'apps.placement.optimizers.conductor.remote_opt_processor.process_placement_opt',
            return_value=mock_req_accept_message)
        self.patcher_RestClient = patch(
            'osdf.utils.interfaces.RestClient', return_value=mock.MagicMock())
        self.Mock_req = self.patcher_req.start()
        self.Mock_req_accept = self.patcher_req_accept.start()
        self.Mock_callback = self.patcher_callback.start()
        self.Mock_RestClient = self.patcher_RestClient.start()

    def tearDown(self):
        patch.stopall()

    def test_process_placement_opt(self):
        main_dir = ""
        conductor_api_template = main_dir + "osdf/templates/conductor_interface.json"
        parameter_data_file = main_dir + "test/placement-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        request_json = json_from_file(parameter_data_file)
        policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]
        local_config = yaml_from_file(local_config_file)
        templ_string = process_placement_opt(request_json, policies, local_config)


    def test_process_placement_opt_placementDemand(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/placement-tests/request_placement.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        request_json = json_from_file(parameter_data_file)
        policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]
        local_config = yaml_from_file(local_config_file)
        templ_string = process_placement_opt(request_json, policies, local_config)        

    def test_process_placement_opt_placementDemand_vfmodule(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/placement-tests/request_vfmod.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        request_json = json_from_file(parameter_data_file)
        policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]
        local_config = yaml_from_file(local_config_file)
        templ_string = process_placement_opt(request_json, policies, local_config)


if __name__ == "__main__":
    unittest.main()


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

import json
import unittest
from requests import RequestException, Response

from apps.slice_selection.optimizers.conductor.remote_opt_processor import process_nsi_selection_opt
from osdf.adapters.local_data import local_policies
from osdf.utils.interfaces import json_from_file, yaml_from_file
from osdf.utils.programming_utils import DotDict
import osdf.config.loader as config_loader
from mock import patch, MagicMock
import json
from osdf.logging.osdf_logging import error_log, debug_log
from osdf.adapters.policy.interface import get_policies


class TestRemoteOptProcessor(unittest.TestCase):
    def setUp(self):
        self.config_spec = {
            "deployment": "config/osdf_config.yaml",
            "core": "config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

    def tearDown(self):
        patch.stopall()

    def test_process_nsi_selection_opt(self):
        main_dir = ""
        request_file = main_dir + 'test/apps/slice_selection/nsi_request.json'
        not_shared_request_file = main_dir + 'test/apps/slice_selection/not_shared_nsi_request.json'
        #response files
        new_solution_response_file = main_dir + 'test/apps/slice_selection/new_solution_nsi_response.json'
        shared_solution_response_file = main_dir + 'test/apps/slice_selection/shared_solution_nsi_response.json'
        no_solution_response_file = main_dir + 'test/apps/slice_selection/no_recomm_nsi_response.json'
        not_shared_response_file = main_dir + 'test/apps/slice_selection/not_shared_nsi_response.json'
        error_response_file = main_dir + 'test/apps/slice_selection/nsi_error_response.json'

        not_shared_request_json = json_from_file(not_shared_request_file)
        not_shared_response_json = json_from_file(not_shared_response_file)
        request_json = json_from_file(request_file)
        new_solution_response_json = json_from_file(new_solution_response_file)
        shared_solution_response_json = json_from_file(shared_solution_response_file)
        no_solution_response_json = json_from_file(no_solution_response_file)
        error_response_json = json_from_file(error_response_file)

        policies_path = main_dir + 'test/policy-local-files'
        slice_policies_file = main_dir + 'test/apps/slice_selection/slice_policies.txt'

        valid_policies_files = local_policies.get_policy_names_from_file(slice_policies_file)
        policies = [json_from_file(policies_path + '/' + name) for name in valid_policies_files]
        self.patcher_get_policies = patch('osdf.adapters.policy.interface.remote_api',
                                          return_value=policies)
        self.Mock_get_policies = self.patcher_get_policies.start()
        # new solution
        new_solution_conductor_response_file = 'test/apps/slice_selection/new_solution_conductor_response.json'
        new_solution_conductor_response = json_from_file(new_solution_conductor_response_file)
        self.patcher_req = patch('osdf.adapters.conductor.conductor.request',
                                 return_value=new_solution_conductor_response)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(new_solution_response_json, process_nsi_selection_opt(request_json, self.osdf_config))
        self.patcher_req.stop()
        # shared solution
        shared_solution_conductor_response_file = 'test/apps/slice_selection/shared_solution_conductor_response.json'
        shared_solution_conductor_response = json_from_file(shared_solution_conductor_response_file)
        self.patcher_req = patch('osdf.adapters.conductor.conductor.request',
                                 return_value=shared_solution_conductor_response)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(shared_solution_response_json,
                          process_nsi_selection_opt(request_json, self.osdf_config))
        self.patcher_req.stop()
        # not-shared solution
        self.assertEquals(not_shared_response_json,
                          process_nsi_selection_opt(not_shared_request_json, self.osdf_config))
        # no recommendation
        no_solution_conductor_response_file = 'test/apps/slice_selection/no_rec.json'
        no_solution_conductor_response = json_from_file(no_solution_conductor_response_file)
        self.patcher_req = patch('osdf.adapters.conductor.conductor.request',
                                 return_value=no_solution_conductor_response)
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(no_solution_response_json,
                          process_nsi_selection_opt(request_json, self.osdf_config))
        self.patcher_req.stop()

        conductor_error_response_file = 'test/apps/slice_selection/conductor_error_response.json'
        conductor_error_response = json_from_file(conductor_error_response_file)

        response = Response()
        response._content = json.dumps(conductor_error_response).encode()
        self.patcher_req = patch('osdf.adapters.conductor.conductor.request',
                                 side_effect=RequestException(response=response))
        self.Mock_req = self.patcher_req.start()
        self.assertEquals(error_response_json, process_nsi_selection_opt(request_json, self.osdf_config))
        self.patcher_req.stop()

        self.patcher_req = patch('osdf.adapters.conductor.conductor.request',
                                 side_effect=Exception("test_exception"))
        self.Mock_req = self.patcher_req.start()
        self.assertEquals('test_exception',
                          process_nsi_selection_opt(request_json, self.osdf_config).get('statusMessage'))
        self.patcher_req.stop()


if __name__ == "__main__":
    unittest.main()


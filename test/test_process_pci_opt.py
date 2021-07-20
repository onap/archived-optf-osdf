# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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
from apps.pci.optimizers.pci_opt_processor import process_pci_optimation
import osdf.config.loader as config_loader
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict


class TestProcessPlacementOpt(unittest.TestCase):

    def setUp(self):
        mock_req_accept_message = Response("Accepted Request", content_type='application/json; charset=utf-8')
        self.patcher_req = patch('apps.pci.optimizers.config_request.request',
                                 return_value={"solutionInfo": {"placementInfo": "dummy"}})
        self.patcher_req_accept = patch('osdf.operation.responses.osdf_response_for_request_accept',
                                        return_value=mock_req_accept_message)
        self.patcher_callback = patch(
            'apps.pci.optimizers.pci_opt_processor.process_pci_optimation',
            return_value=mock_req_accept_message)

        mock_mzn_response = [{'pci': {0: 0, 1: 1, 2: 2}}]

        self.patcher_minizinc_callback = patch(
            'apps.pci.optimizers.solver.optimizer.solve',
            return_value=mock_mzn_response )
        self.patcher_RestClient = patch(
            'osdf.utils.interfaces.RestClient', return_value=mock.MagicMock())
        self.Mock_req = self.patcher_req.start()
        self.Mock_req_accept = self.patcher_req_accept.start()
        self.Mock_callback = self.patcher_callback.start()
        self.Mock_RestClient = self.patcher_RestClient.start()
        self.Mock_mzn_callback = self.patcher_minizinc_callback.start()

    def tearDown(self):
        patch.stopall()

    def test_process_pci_opt_solutions(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/pci-optimization-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        self.config_spec = {
            "deployment": "test/functest/simulators/simulated-config/osdf_config.yaml",
            "core": "test/functest/simulators/simulated-config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

        valid_policies_list_file = policy_data_path + '/' + 'meta-valid-policies.txt'
        valid_policies_files = local_policies.get_policy_names_from_file(valid_policies_list_file)

        request_json = json_from_file(parameter_data_file)
        policies = [json_from_file(policy_data_path + '/' + name) for name in valid_policies_files]

        templ_string = process_pci_optimation(request_json, self.osdf_config,policies)


if __name__ == "__main__":
    unittest.main()


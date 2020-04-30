import unittest
from unittest.mock import patch
from apps.nst.optimizers.nst_select_processor import process_nst_selection
import osdf.config.loader as config_loader
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict


class test_nst_selection_solution(unittest.TestCase):

    @patch('apps.nst.optimizers.nst_select_processor.get_policies')
    @patch('apps.nst.optimizers.nst_select_processor.conductor.request')
    def test_nst_selection_solutions( self, mock_conductor, mock_policy):

        self.config_spec = {
        "deployment": "test/functest/simulators/simulated-config/osdf_config.yaml",
        "core": "test/functest/simulators/simulated-config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))
        main_dir = ""
        conductor_file = main_dir + "test/nst_selection/conductor.json"
        policy_file =  main_dir + "test/nst_selection/policies.json"
        request_file = main_dir + "test/nst_selection/request.json"
        result_file = main_dir + "test/nst_selection/result.json"
        mock_policy.return_value = json_from_file(policy_file)
        mock_conductor.return_value = json_from_file(conductor_file)
        request_json = json_from_file(request_file)
        actual_result = json_from_file(result_file)
        mock_result = process_nst_selection(request_json, self.osdf_config)
        self.assertEqual(mock_result, actual_result)

if __name__ == '__main__':
    unittest.main()
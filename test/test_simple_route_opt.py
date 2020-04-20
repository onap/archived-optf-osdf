from apps.route.optimizers.simple_route_opt import RouteOpt
from osdf.utils.interfaces import json_from_file
from unittest.mock import patch
import osdf.config.loader as config_loader
from osdf.utils.programming_utils import DotDict
import unittest


class TestSimpleRouteOptimization(unittest.TestCase):
    @patch('apps.route.optimizers.simple_route_opt.requests.get')
    @patch('apps.route.optimizers.simple_route_opt.pymzn.minizinc')
    def test_process_nst_selection_solutions( self, mock_solve, mock_get):

        main_dir = ""
        response_data_file = main_dir + "test/simple_route_opt/AAI.json"
        mock_get.return_value.json.return_value = json_from_file(response_data_file)
        mock_get.return_value.status_code = 200
        mock_solve.return_value = [{'x': [1, 1, 1]}]
        self.config_spec = {
            "deployment": "test/functest/simulators/simulated-config/osdf_config.yaml",
            "core": "test/functest/simulators/simulated-config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))
        parameter_data_file = main_dir + "test/simple_route_opt/routeOpt.json"
        request_json = json_from_file(parameter_data_file)
        mock_response = {
            "requestId": "yyy-yyy-yyyy",
            "requestStatus": "accepted",
            "solutions": [
                {
                    "end_node": "10.10.10.10",
                    "link": "link-id-1",
                    "start_node": "20.20.20.20"
                },
                {
                    "end_node": "11.11.11.11",
                    "link": "link-id-2",
                    "start_node": "22.22.22.22"
                },
                {
                    "end_node": "20.20.20.20",
                    "link": "link-id-3",
                    "start_node": "11.11.11.11"
                }
            ],
            "statusMessage": " ",
            "transactionId": "xxx-xxx-xxxx"
        }
        routopt = RouteOpt()
        actual_response = routopt.getRoute(request_json,self.osdf_config)
        self.assertEqual(mock_response, actual_response)



if __name__ == '__main__':
    unittest.main()


from apps.route.optimizers.simple_route_opt import RouteOpt
from osdf.utils.interfaces import json_from_file
from unittest.mock import patch
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
        parameter_data_file = main_dir + "test/simple_route_opt/routeOpt.json"
        request_json = json_from_file(parameter_data_file)
        mock_response = {"requestId":"yyy-yyy-yyyy","requestStatus":"accepted","solutions":["link-id-1","link-id-2","link-id-3"],"statusMessage":" ","transactionId":"xxx-xxx-xxxx"}
        routopt = RouteOpt()
        actual_response = routopt.getRoute(request_json)
        self.assertEqual(mock_response, actual_response)



if __name__ == '__main__':
    unittest.main()


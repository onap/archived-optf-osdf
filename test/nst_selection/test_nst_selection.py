from apps.nst.optimizers.nst_select_processor import process_nst_selection
from osdf.utils.interfaces import json_from_file
import unittest

class TestNstSelection(unittest.TestCase):
    def test_process_nst_selection_solutions(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/nst_selection/request.json"
        request_json = json_from_file(parameter_data_file)
        mock_response = {'requestStatus': 'accepted', 'statusMessage': ' ', 'transactionId': 'xxx-xxx-xxxx', 'solutions': {'NSTsolution': {'invariantUUID': 'INvariant UUID', 'UUID': 'uuid', 'matchLevel': 1, 'NSTName': 'NST_1'}}, 'requestId': 'yyy-yyy-yyyy'}
        actual_response = process_nst_selection(request_json,None)
        self.assertEqual(mock_response, actual_response)



if __name__ == '__main__':
    unittest.main()
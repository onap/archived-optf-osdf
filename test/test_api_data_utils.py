import json
import os
from osdf.utils import api_data_utils
from collections import defaultdict


BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "placement-tests/request.json")) as json_data:
    req_json = json.load(json_data)

class TestVersioninfo():
#
# Tests for api_data_utils.py
#   
    def test_retrieve_version_info(self):
        request_id = 'test12345'
        test_dict = {'placementVersioningEnabled': False, 'placementMajorVersion': '1', 'placementPatchVersion': '0', 'placementMinorVersion': '0'}
        test_verison_info_dict = defaultdict(dict ,test_dict )
        #verison_info_dict = api_data_utils.retrieve_version_info(req_json, request_id)
        #assert verison_info_dict == test_verison_info_dict

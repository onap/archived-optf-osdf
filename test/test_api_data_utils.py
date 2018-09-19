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
        verison_info_dict = api_data_utils.retrieve_version_info(req_json, request_id)
        assert verison_info_dict == test_verison_info_dict
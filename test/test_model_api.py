# -------------------------------------------------------------------------
#   Copyright (c) 2020 AT&T Intellectual Property
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

import pytest
from mock import patch
from schematics.exceptions import DataError

from runtime.model_api import create_model_data, get_model_data, delete_model_data, retrieve_all_models
from runtime.models.api.model_request import OptimModelRequestAPI
from runtime.optim_engine import validate_request

BASE_DIR = os.path.dirname(__file__)

ret_val = {'modelId': 'test', 'description': 'desc', 'solver': 'mzn'}


class TestModelApi():

    def test_valid_mapi_request(self):
        req_json = json.loads(open("./test/optengine-tests/test_modelapi_valid.json").read())

        assert OptimModelRequestAPI(req_json).validate() is None

    def test_invalid_mapi_request(self):
        req_json = json.loads(open("./test/optengine-tests/test_modelapi_invalid.json").read())
        with pytest.raises(DataError):
            validate_request(req_json)

    @patch('runtime.model_api.build_model_dict')
    @patch('mysql.connector.connect')
    @patch('runtime.model_api.osdf_config')
    def test_create_model(self, config, conn, model_data):
        model_data.return_value = ret_val
        req_json = json.loads(open("./test/optengine-tests/test_modelapi_valid.json").read())

        create_model_data(req_json)

    @patch('runtime.model_api.build_model_dict')
    @patch('mysql.connector.connect')
    @patch('runtime.model_api.osdf_config')
    def test_retrieve_model(self, config, conn, model_data):
        model_data.return_value = ret_val
        get_model_data('test')

    @patch('mysql.connector.connect')
    @patch('runtime.model_api.osdf_config')
    def test_delete_model(self, config, conn):
        delete_model_data('test')

    @patch('mysql.connector.connect')
    @patch('runtime.model_api.osdf_config')
    def test_retrieve_all_model(self, config, conn):
        retrieve_all_models()

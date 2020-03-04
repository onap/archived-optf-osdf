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

from osdf.operation.exceptions import BusinessException
from runtime.optim_engine import validate_request, process_request

BASE_DIR = os.path.dirname(__file__)


class TestOptimEngine():

    def test_valid_optim_request(self):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_valid.json").read())

        assert validate_request(req_json) == True

    def test_invalid_optim_request(self):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_invalid.json").read())
        with pytest.raises(DataError):
            validate_request(req_json)

    def test_invalid_optim_request_without_modelid(self):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_invalid2.json").read())
        with pytest.raises(BusinessException):
            validate_request(req_json)

    def test_invalid_optim_request_no_optdata(self):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_no_optdata.json").read())
        with pytest.raises(BusinessException):
            validate_request(req_json)

    def test_process_request(self):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_valid.json").read())

        res = process_request(req_json)
        assert res.status_code == 400

    def test_py_process_request(self):
        req_json = json.loads(open("./test/optengine-tests/test_py_optengine_valid.json").read())

        res = process_request(req_json)
        assert res.status_code == 200

    def test_invalid_solver(self):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_invalid_solver.json").read())

        with pytest.raises(BusinessException):
            process_request(req_json)

    @patch('runtime.optim_engine.get_model_data')
    def test_process_solverid_request(self, mocker):
        req_json = json.loads(open("./test/optengine-tests/test_optengine_modelId.json").read())

        data = 200, ('junk', '', '', 'py')
        mocker.return_value = data
        process_request(req_json)

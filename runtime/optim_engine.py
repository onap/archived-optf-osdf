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

from flask import Response

from osdf.operation.exceptions import BusinessException
from osdf.utils.data_conversion import decode_data
from .model_api import get_model_data
from .models.api.optim_request import OptimizationAPI
from .solvers.mzn.mzn_solver import solve as mzn_solve
from .solvers.py.py_solver import solve as py_solve


def is_valid_optim_request(request_json):
    # Method to check whether the requestinfo/optimizer value is valid.
    opt_info = request_json['optimInfo']
    if not opt_info.get('modelId'):
        if not opt_info.get('modelContent') or not opt_info.get('solver'):
            raise BusinessException('modelContent and solver needs to be populated if model_id is not set')
    if not opt_info.get('optData'):
        raise BusinessException('optimInfo.optData needs to be populated to solve for a problem')

    return True


def validate_request(request_json):
    OptimizationAPI(request_json).validate()
    if not is_valid_optim_request(request_json):
        raise BusinessException('Invalid optim request ')
    return True


def process_request(request_json):
    response_code, response_message = run_optimizer(request_json)
    response = Response(response_message, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(response_message))
    response.status_code = response_code
    return response


def run_optimizer(request_json):
    validate_request(request_json)

    model_content, solver = get_model_content(request_json)

    if solver == 'mzn':
        return mzn_solve(request_json, model_content)
    elif solver == 'py':
        return py_solve(request_json, model_content)
    raise BusinessException('Unsupported optimization solver requested {} '.format(solver))


def get_model_content(request_json):
    model_id = request_json['optimInfo'].get('modelId')
    if model_id:
        status, data = get_model_data(model_id)
        if status == 200:
            model_content = decode_data(data[1])
            solver = data[3]
        else:
            raise BusinessException('model_id [{}] not found in the model database'.format(model_id))
    else:
        model_content = request_json['optimInfo']['modelContent']
        solver = request_json['optimInfo']['solver']
    return model_content, solver

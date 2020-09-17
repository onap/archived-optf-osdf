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

from datetime import datetime
import json

from pymzn import cbc
from pymzn import chuffed
from pymzn import gecode
from pymzn import minizinc
from pymzn import or_tools
from pymzn import Status

from osdf.utils.file_utils import delete_file_folder

error_status_map = {
    Status.INCOMPLETE: "incomplete",
    Status.COMPLETE: "complete",
    Status.UNSATISFIABLE: "unsatisfiable",
    Status.UNKNOWN: "unknown",
    Status.UNBOUNDED: "unbounded",
    Status.UNSATorUNBOUNDED: "unsat_or_unbounded",
    Status.ERROR: "error"
}

solver_dict = {
    'cbc': cbc,
    'geocode': gecode,
    'chuffed': chuffed,
    'cp': chuffed,
    'or_tools': or_tools
}


def map_status(status):
    return error_status_map.get(status, "failed")


def solve(request_json, mzn_content):
    """Given the request and minizinc content.  Translates the json request
    to the format minizinc understands

    return: returns the optimized solution.
    """
    req_info = request_json['requestInfo']
    opt_info = request_json['optimInfo']
    try:
        mzn_solution = mzn_solver(mzn_content, opt_info)

        response = {
            'transactionId': req_info['transactionId'],
            'requestID': req_info['requestID'],
            'requestStatus': 'done',
            'statusMessage': map_status(mzn_solution.status),
            'solutions': mzn_solution[0] if mzn_solution else {}
        }
        return 200, json.dumps(response)
    except Exception as e:
        response = {
            'transactionId': req_info['transactionId'],
            'requestID': req_info['requestID'],
            'requestStatus': 'failed',
            'statusMessage': 'Failed due to {}'.format(e)
        }
        return 400, json.dumps(response)


def mzn_solver(mzn_content, opt_info):
    """Calls the minizinc optimizer.

    """
    args = opt_info['solverArgs']
    solver = get_mzn_solver(args.pop('solver'))
    mzn_opts = dict()

    try:
        file_name = persist_opt_data(opt_info)
        mzn_opts.update(args)
        return minizinc(mzn_content, file_name, **mzn_opts, solver=solver)

    finally:
        delete_file_folder(file_name)


def persist_opt_data(opt_info):
    """Persist the opt data, if included as part of the request.

    return: file_name path of the optim_data
            returns None if no optData is part of the request
    """
    file_name = None
    if 'optData' in opt_info:
        if opt_info['optData'].get('json'):
            data_content = json.dumps(opt_info['optData']['json'])
            file_name = '/tmp/optim_engine_{}.json'.format(datetime.timestamp(datetime.now()))
            persist_data(data_content, file_name)
        elif opt_info['optData'].get('text'):
            data_content = opt_info['optData']['text']
            file_name = '/tmp/optim_engine_{}.dzn'.format(datetime.timestamp(datetime.now()))
            persist_data(data_content, file_name)
    return file_name


def persist_data(data_content, file_name):
    """Save the dzn data into a file

    """
    with open(file_name, "wt") as data:
        data.write(data_content)


def get_mzn_solver(solver):
    """Returns a solver type object for minizinc optimizers

    solver: solver that is part of the request
    return: solver mapped object
    """
    return solver_dict.get(solver)

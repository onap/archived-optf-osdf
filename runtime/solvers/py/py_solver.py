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
import subprocess
import traceback
from datetime import datetime

from osdf.logging.osdf_logging import error_log, debug_log
from osdf.utils.file_utils import delete_file_folder


def py_solver(py_content, opt_info):
    py_file = '/tmp/custom_heuristics_{}.py'.format(datetime.timestamp(datetime.now()))
    with open(py_file, "wt") as f:
        f.write(py_content)
    if opt_info['optData'].get('json'):
        data_content = json.dumps(opt_info['optData']['json'])
        input_file = '/tmp/optim_engine_{}.json'.format(datetime.timestamp(datetime.now()))
    elif opt_info['optData'].get('text'):
        data_content = opt_info['optData']['text']
        input_file = '/tmp/optim_engine_{}.txt'.format(datetime.timestamp(datetime.now()))
    with open(input_file, "wt") as f:
        f.write(data_content)

    output_file = '/tmp/opteng_output_{}.json'.format(datetime.timestamp(datetime.now()))

    command = ['python', py_file, input_file, output_file]

    try:
        p = subprocess.run(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

        debug_log.debug('Process return code {}'.format(p.returncode))
        if p.returncode > 0:
            error_log.error('Process return code {} {}'.format(p.returncode, p.stdout))
            return 'error', {}
        with open(output_file) as file:
            data = file.read()
            return 'success', json.loads(data)

    except Exception as e:
        error_log.error("Error running optimizer {}".format(traceback.format_exc()))
        return 'error', {}
    finally:
        cleanup((input_file, output_file, py_file))


def cleanup(file_tup):
    for f in file_tup:
        try:
            delete_file_folder(f)
        except Exception as e:
            error_log.error("Failed deleting the file {} - {}".format(f, traceback.format_exc()))


def solve(request_json, py_content):
    req_info = request_json['requestInfo']
    opt_info = request_json['optimInfo']
    try:
        status, solution = py_solver(py_content, opt_info)

        response = {
            'transactionId': req_info['transactionId'],
            'requestID': req_info['requestID'],
            'requestStatus': status,
            'statusMessage': "completed",
            'solutions': solution if solution else {}
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

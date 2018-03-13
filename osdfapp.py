# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

"""
OSDF Manager Main Flask Application
"""

import sys
from threading import Thread  # for scaling up, may need celery with RabbitMQ or redis

from flask import Flask, request, Response, g

import osdf
import pydevd
import json
import osdf.adapters.policy.interface
import osdf.config.credentials
import osdf.config.loader
import osdf.operation.error_handling
import osdf.operation.responses
import traceback
from osdf.adapters.policy.interface import get_policies
from osdf.config.base import osdf_config
from osdf.optimizers.placementopt.conductor.remote_opt_processor import process_placement_opt
from osdf.webapp.appcontroller import auth_basic
from optparse import OptionParser
from osdf.operation.exceptions import BusinessException
from osdf.operation.error_handling import request_exception_to_json_body, internal_error_message
from requests import RequestException
from schematics.exceptions import DataError
from osdf.logging.osdf_logging import MH, audit_log, error_log
from osdf.models.api.placementRequest import PlacementAPI

ERROR_TEMPLATE = osdf.ERROR_TEMPLATE

app = Flask(__name__)



BAD_CLIENT_REQUEST_MESSAGE = 'Client sent an invalid request'

# An exception explicitly raised due to some business rule
@app.errorhandler(BusinessException)
def handle_business_exception(e):
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    err_msg = ERROR_TEMPLATE.render(description=str(e))
    response = Response(err_msg, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response

# Returns a detailed synchronous message to the calling client when osdf fails due to a remote call to another system
@app.errorhandler(RequestException)
def handle_request_exception(e):
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    err_msg = request_exception_to_json_body(e)
    response = Response(err_msg, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response

# Returns a detailed message to the calling client when the initial synchronous message is invalid
@app.errorhandler(DataError)
def handle_data_error(e):
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))

    body_dictionary = {
        "serviceException": {
            "text": BAD_CLIENT_REQUEST_MESSAGE,
            "exceptionMessage": str(e.messages),
            "errorType": "InvalidClientRequest"
        }
    }

    body_as_json = json.dumps(body_dictionary)
    response = Response(body_as_json, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response


@app.route("/api/oof/v1/placement", methods=["POST"])
@auth_basic.login_required
def do_placement_opt():
    """Perform placement optimization after validating the request and fetching policies
    Make a call to the call-back URL with the output of the placement request.
    Note: Call to Conductor for placement optimization may have redirects, so account for them
    """
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))

    PlacementAPI(request_json).validate()

    # Currently policies are being used only during placement, so only fetch them if placement demands is not empty
    policies = {}

    if 'placementDemand' in request_json['placementInfo']['demandInfo']:
        policies, prov_status = get_policies(request_json, "placement")

    audit_log.info(MH.new_worker_thread(req_id, "[for placement]"))
    t = Thread(target=process_placement_opt, args=(request_json, policies, osdf_config, prov_status))
    t.start()
    audit_log.info(MH.accepted_valid_request(req_id, request))
    return osdf.operation.responses.osdf_response_for_request_accept(
        req_id=req_id, text="Accepted placement request. Response will be posted to callback URL")


# Returned when unexpected coding errors occur during initial synchronous processing
@app.errorhandler(500)
def internal_failure(error):
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    response = Response(internal_error_message, content_type='application/json; charset=utf-8')
    response.status_code = 500
    return response


def get_options(argv):
    program_version_string = '%%prog %s' % ("v1.0")
    program_longdesc = ""
    program_license = ""

    parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
    parser.add_option("-l", "--local", dest="local", help="run locally", action="store_true", default=False)
    parser.add_option("-t", "--devtest", dest="devtest", help="run in dev/test environment", action="store_true", default=False)
    parser.add_option("-d", "--debughost", dest="debughost", help="IP Address of host running debug server", default='')
    parser.add_option("-p", "--debugport", dest="debugport", help="Port number of debug server", type=int, default=5678)
    (opts, args) = parser.parse_args(argv)

    if (opts.debughost != ''):
        print('pydevd.settrace(%s, port=%s)' % (opts.debughost, opts.debugport))
        pydevd.settrace(opts.debughost, port=opts.debugport)
    return opts


if __name__ == "__main__":

    sys_conf = osdf_config['core']['osdf_system']
    ports = sys_conf['osdf_ports']
    internal_port, external_port = ports['internal'], ports['external']
    ssl_context = tuple(sys_conf['ssl_context'])
    local_host = "0.0.0.0"  # NOSONAR

    common_app_opts = dict(host=local_host, threaded=True, use_reloader=False)

    opts = get_options(sys.argv)
    if (not opts.local and not opts.devtest):  # normal deployment
        app.run(port=internal_port, ssl_context=ssl_context, debug=False, **common_app_opts)
    else:
        port = internal_port if opts.local else external_port
        app.run(port=port, debug=True, **common_app_opts)

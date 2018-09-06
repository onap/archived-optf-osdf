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
from requests.auth import HTTPBasicAuth

import osdf
import pydevd
import json
import osdf.adapters.policy.interface
import osdf.config.credentials
import osdf.config.loader
import osdf.operation.error_handling
import osdf.operation.responses
import requests
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
from osdf.logging.osdf_logging import MH, audit_log, error_log, debug_log
from osdf.models.api.placementRequest import PlacementAPI
from osdf.models.api.pciOptimizationRequest import PCIOptimizationAPI
from osdf.operation.responses import osdf_response_for_request_accept as req_accept
from osdf.optimizers.routeopt.simple_route_opt import RouteOpt
from osdf.optimizers.pciopt.pci_opt_processor import process_pci_optimation
from osdf.utils import api_data_utils

ERROR_TEMPLATE = osdf.ERROR_TEMPLATE

app = Flask(__name__)

BAD_CLIENT_REQUEST_MESSAGE = 'Client sent an invalid request'


@app.errorhandler(BusinessException)
def handle_business_exception(e):
    """An exception explicitly raised due to some business rule"""
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    err_msg = ERROR_TEMPLATE.render(description=str(e))
    response = Response(err_msg, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response


@app.errorhandler(RequestException)
def handle_request_exception(e):
    """Returns a detailed synchronous message to the calling client
    when osdf fails due to a remote call to another system"""
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    err_msg = request_exception_to_json_body(e)
    response = Response(err_msg, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response


@app.errorhandler(DataError)
def handle_data_error(e):
    """Returns a detailed message to the calling client when the initial synchronous message is invalid"""
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))

    body_dictionary = {
        "serviceException": {
            "text": BAD_CLIENT_REQUEST_MESSAGE,
            "exceptionMessage": str(e.errors),
            "errorType": "InvalidClientRequest"
        }
    }

    body_as_json = json.dumps(body_dictionary)
    response = Response(body_as_json, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response


@app.route("/api/oof/v1/healthcheck", methods=["GET"])
def do_osdf_health_check():
    """Simple health check"""
    audit_log.info("A health check request is processed!")
    return "OK"


@app.route("/api/oof/v1/placement", methods=["POST"])
@auth_basic.login_required
def do_placement_opt():
    return placement_rest_api()


@app.route("/api/oof/placement/v1", methods=["POST"])
@auth_basic.login_required
def do_placement_opt_common_versioning():
    return placement_rest_api()


def placement_rest_api():
    """Perform placement optimization after validating the request and fetching policies
    Make a call to the call-back URL with the output of the placement request.
    Note: Call to Conductor for placement optimization may have redirects, so account for them
    """
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))
    api_version_info = api_data_utils.retrieve_version_info(request, req_id)
    PlacementAPI(request_json).validate()
    policies = get_policies(request_json, "placement")
    audit_log.info(MH.new_worker_thread(req_id, "[for placement]"))
    t = Thread(target=process_placement_opt, args=(request_json, policies, osdf_config))
    t.start()
    audit_log.info(MH.accepted_valid_request(req_id, request))
    return req_accept(request_id=req_id,
                      transaction_id=request_json['requestInfo']['transactionId'],
                      version_info=api_version_info, request_status="accepted", status_message="")


@app.route("/api/oof/v1/route", methods=["POST"])
def do_route_calc():
    """
    Perform the basic route calculations and returnn the vpn-bindings
    """
    request_json = request.get_json()
    audit_log.info("Calculate Route request received!")
    return RouteOpt().getRoute(request_json)

@app.route("/api/oof/v1/pci", methods=["POST"])
@auth_basic.login_required
def do_pci_optimization():
    request_json = request.get_json()
    req_id = request_json['requestInfo']['requestId']
    g.request_id = req_id
    audit_log.info(MH.received_request(request.url, request.remote_addr, json.dumps(request_json)))
    PCIOptimizationAPI(request_json).validate()
    policies = get_policies(request_json, "pciopt")
    audit_log.info(MH.new_worker_thread(req_id, "[for pciopt]"))
    t = Thread(target=process_pci_optimation, args=(request_json, policies, osdf_config))
    t.start()
    audit_log.info(MH.accepted_valid_request(req_id, request))
    return req_accept(request_id=req_id,
                      transaction_id=request_json['requestInfo']['transactionId'],
                      request_status="accepted", status_message="")

@app.errorhandler(500)
def internal_failure(error):
    """Returned when unexpected coding errors occur during initial synchronous processing"""
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    response = Response(internal_error_message, content_type='application/json; charset=utf-8')
    response.status_code = 500
    return response

def get_options(argv):
    program_version_string = '%%prog %s' % "v1.0"
    program_longdesc = ""
    program_license = ""

    parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
    parser.add_option("-l", "--local", dest="local", help="run locally", action="store_true", default=False)
    parser.add_option("-t", "--devtest", dest="devtest", help="run in dev/test environment", action="store_true",
                      default=False)
    parser.add_option("-d", "--debughost", dest="debughost", help="IP Address of host running debug server", default='')
    parser.add_option("-p", "--debugport", dest="debugport", help="Port number of debug server", type=int, default=5678)
    opts, args = parser.parse_args(argv)

    if opts.debughost:
        debug_log.debug('pydevd.settrace({}, port={})'.format(opts.debughost, opts.debugport))
        pydevd.settrace(opts.debughost, port=opts.debugport)
    return opts


if __name__ == "__main__":

    sys_conf = osdf_config['core']['osdf_system']
    ports = sys_conf['osdf_ports']
    internal_port, external_port = ports['internal'], ports['external']

    local_host = sys_conf['osdf_ip_default']
    common_app_opts = dict(host=local_host, threaded=True, use_reloader=False)

    ssl_opts = sys_conf.get('ssl_context')
    if ssl_opts:
        common_app_opts.update({'ssl_context': tuple(ssl_opts)})

    opts = get_options(sys.argv)
    if not opts.local and not opts.devtest:  # normal deployment
        app.run(port=internal_port, debug=False, **common_app_opts)
    else:
        port = internal_port if opts.local else external_port
        app.run(port=port, debug=True, **common_app_opts)

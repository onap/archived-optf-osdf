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

import json
import ssl
import sys
import time
import traceback
from optparse import OptionParser

import pydevd
from flask import Flask, request, Response, g
from requests import RequestException
from schematics.exceptions import DataError

import osdf.adapters.aaf.sms as sms
import osdf.operation.responses
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import error_log, debug_log
from osdf.operation.error_handling import request_exception_to_json_body, internal_error_message
from osdf.operation.exceptions import BusinessException
from osdf.utils.mdc_utils import clear_mdc, mdc_from_json, default_mdc

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


@app.before_request
def log_request():
    g.request_start = time.clock()
    if request.get_json():

        request_json = request.get_json()
        g.request_id = request_json['requestInfo']['requestId']
        mdc_from_json(request_json)
    else:
        g.request_id = "N/A"
        default_mdc()



@app.after_request
def log_response(response):
    clear_mdc()
    return response


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


def build_ssl_context():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.set_ciphers('ECDHE-RSA-AES128-SHA256:EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH')
    ssl_context.load_cert_chain(sys_conf['ssl_context'][0], sys_conf['ssl_context'][1])
    return ssl_context


def run_app():
    global sys_conf
    sys_conf = osdf_config['core']['osdf_system']
    ports = sys_conf['osdf_ports']
    internal_port, external_port = ports['internal'], ports['external']
    local_host = sys_conf['osdf_ip_default']
    common_app_opts = dict(host=local_host, threaded=True, use_reloader=False)
    ssl_opts = sys_conf.get('ssl_context')
    if ssl_opts:
        common_app_opts.update({'ssl_context': build_ssl_context()})
    opts = get_options(sys.argv)
    # Load secrets from SMS
    sms.load_secrets()
    if not opts.local and not opts.devtest:  # normal deployment
        app.run(port=internal_port, debug=False, **common_app_opts)
    else:
        port = internal_port if opts.local else external_port
        app.run(port=port, debug=True, **common_app_opts)


if __name__ == "__main__":
    run_app()

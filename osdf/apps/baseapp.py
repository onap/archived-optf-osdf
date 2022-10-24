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
from optparse import OptionParser
import ssl
import sys
import time
import traceback

from flask import Flask
from flask import g
from flask import request
from flask import Response
from onaplogging.mdcContext import MDC
from requests import RequestException
from schematics.exceptions import DataError

import osdf.adapters.aaf.sms as sms
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import audit_log
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import error_log
from osdf.operation.error_handling import internal_error_message
from osdf.operation.error_handling import request_exception_to_json_body
from osdf.operation.exceptions import BusinessException
import osdf.operation.responses
from osdf.utils.mdc_utils import clear_mdc
from osdf.utils.mdc_utils import get_request_id
from osdf.utils.mdc_utils import populate_default_mdc
from osdf.utils.mdc_utils import populate_mdc
from osdf.utils.mdc_utils import set_error_details

ERROR_TEMPLATE = osdf.ERROR_TEMPLATE

app = Flask(__name__)

BAD_CLIENT_REQUEST_MESSAGE = 'Client sent an invalid request'


@app.errorhandler(BusinessException)
def handle_business_exception(e):
    """An exception explicitly raised due to some business rule

    """
    error_log.error("Synchronous error for request id {} {}"
                    .format(g.request_id, traceback.format_exc()))
    err_msg = ERROR_TEMPLATE.render(description=str(e))
    response = Response(err_msg, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response


@app.errorhandler(RequestException)
def handle_request_exception(e):
    """Returns a detailed synchronous message to the calling client when osdf fails due to a remote call to another system

    """
    error_log.error("Synchronous error for request id {} {}".format(g.request_id, traceback.format_exc()))
    err_msg = request_exception_to_json_body(e)
    response = Response(err_msg, content_type='application/json; charset=utf-8')
    response.status_code = 400
    return response


@app.errorhandler(DataError)
def handle_data_error(e):
    """Returns a detailed message to the calling client when the initial synchronous message is invalid

    """
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
    clear_mdc()
    if request.content_type and 'json' in request.content_type:
        populate_mdc(request)
        g.request_id = get_request_id(request.get_json())
        log_message(json.dumps(request.get_json()), "INPROGRESS", 'ENTRY')
    else:
        populate_default_mdc(request)
        log_message('', "INPROGRESS", 'ENTRY')


@app.after_request
def log_response(response):
    log_response_data(response)
    return response


def log_response_data(response):
    status_value = ''
    try:
        status_value = map_status_value(response)
        log_message(response.get_data(as_text=True), status_value, 'EXIT')
    except Exception:
        try:
            set_default_audit_mdc(request, status_value, 'EXIT')
            audit_log.info(response.get_data(as_text=True))
        except Exception:
            set_error_details(300, 'Internal Error')
            error_log.error("Error logging the response data due to {}".format(traceback.format_exc()))


def set_default_audit_mdc(request, status_value, p_marker):
    MDC.put('partnerName', 'internal')
    MDC.put('serviceName', request.path)
    MDC.put('statusCode', status_value)
    MDC.put('requestID', 'internal')
    MDC.put('timer', int((time.process_time() - g.request_start) * 1000))
    MDC.put('customField1', p_marker)


def log_message(message, status_value, p_marker='INVOKE'):
    MDC.put('statusCode', status_value)
    MDC.put('customField1', p_marker)
    MDC.put('timer', int((time.process_time() - g.request_start) * 1000))
    audit_log.info(message)


def map_status_value(response):
    if 200 <= response.status_code < 300:
        status_value = "COMPLETE"
    else:
        status_value = "ERROR"
    return status_value


@app.errorhandler(500)
def internal_failure(error):
    """Returned when unexpected coding errors occur during initial synchronous processing

    """
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
    parser.add_option("-d", "--debughost", dest="debughost",
                      help="IP Address of host running debug server", default='')
    parser.add_option("-p", "--debugport", dest="debugport",
                      help="Port number of debug server", type=int, default=5678)
    opts, args = parser.parse_args(argv)

    if opts.debughost:
        debug_log.debug('pydevd.settrace({}, port={})'.format(opts.debughost, opts.debugport))
        # pydevd.settrace(opts.debughost, port=opts.debugport)
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
    is_aaf_enabled = osdf_config.deployment.get('is_aaf_enabled', False)
    if is_aaf_enabled:
        # Load secrets from SMS
        sms.load_secrets()
    if not opts.local and not opts.devtest:  # normal deployment
        app.run(port=internal_port, debug=False, **common_app_opts)
    else:
        port = internal_port if opts.local else external_port
        app.run(port=port, debug=True, **common_app_opts)


if __name__ == "__main__":
    run_app()

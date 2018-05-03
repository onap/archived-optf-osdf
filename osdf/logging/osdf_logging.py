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

import traceback
import uuid

from .ecomp_common_v1.CommonLogger import CommonLogger
from osdf.utils.programming_utils import MetaSingleton


def log_handlers_pre_onap(config_file="config/onap_logging_common_v1.config",
                          service_name="OOF_OSDF"):
    """
    Convenience handlers for logging to different log files

    :param config_file: configuration file (properties file) that specifies log location, rotation, etc.
    :param service_name: name for this service
    :return: dictionary of log objects: "error", "metrics", "audit", "debug"

    We can use the returned values as follows:
    X["error"].fatal("a FATAL message for the error log")
    X["error"].error("an ERROR message for the error log")
    X["error"].warn("a WARN message for the error log")
    X["audit"].info("an INFO message for the audit log")
    X["metrics"].info("an INFO message for the metrics log")
    X["debug"].debug("a DEBUG message for the debug log")
    """
    main_params = dict(instanceUUID=uuid.uuid1(), serviceName=service_name, configFile=config_file)
    return dict((x, CommonLogger(logKey=x, **main_params))
                for x in ["error", "metrics", "audit", "debug"])


def format_exception(err, prefix=None):
    """Format operation for use with ecomp logging
    :param err: exception object
    :param prefix: prefix string message
    :return: formatted exception (via repr(traceback.format_tb(err.__traceback__))
    """
    exception_lines = traceback.format_exception(err.__class__, err, err.__traceback__)
    exception_desc = "".join(exception_lines)
    return exception_desc if not prefix else prefix + ": " + exception_desc


class OOF_OSDFLogMessageHelper(metaclass=MetaSingleton):
    """Provides loggers as a singleton (otherwise, we end up with duplicate messages).
    Provides error_log, metric_log, audit_log, and debug_log (in that order)
    Additionally can provide specific log handlers too
    """
    log_handlers = None
    default_levels = ["error", "metrics", "audit", "debug"]

    def _setup_handlers(self, log_version="pre_onap", config_file=None, service_name=None):
        """return error_log, metrics_log, audit_log, debug_log"""
        if self.log_handlers is None:
            params = {}
            params.update({"config_file": config_file} if config_file else {})
            params.update({"service_name": service_name} if service_name else {})

            if log_version == "pre_onap":
                self.log_handlers = log_handlers_pre_onap(**params)

    def get_handlers(self, levels=None, log_version="pre_onap", config_file=None, service_name=None):
        """Return ONAP-compliant log handlers for different levels. Each "level" ends up in a different log file
        with a prefix of that level.

        For example: error_log, metrics_log, audit_log, debug_log in that order
        :param levels: None or list of levels subset of self.default_levels (["error", "metrics", "audit", "debug"])
        :param log_version: Currently only pre_onap is supported
        :param config_file: Logging configuration file for ONAP compliant logging
        :param service_name: Name of the service
        :return: list of log_handlers in the order of levels requested.
              if levels is None: we return handlers for self.default_levels
              if levels is ["error", "audit"], we return log handlers for that.
        """
        self._setup_handlers(log_version="pre_onap", config_file=config_file, service_name=service_name)
        wanted_levels = self.default_levels if levels is None else levels
        return [self.log_handlers.get(x) for x in wanted_levels]


class OOF_OSDFLogMessageFormatter(object):

    @staticmethod
    def accepted_valid_request(req_id, request):
        return "Accepted valid request for ID: {} for endpoint: {}".format(
            req_id, request.url)

    @staticmethod
    def invalid_request(req_id, err):
        return "Invalid request for request ID: {}; cause: {}".format(
            req_id, format_exception(err))

    @staticmethod
    def invalid_response(req_id, err):
        return "Invalid response for request ID: {}; cause: {}".format(
            req_id, format_exception(err))

    @staticmethod
    def malformed_request(request, err):
        return "Malformed request for URL {}, from {}; cause: {}".format(
            request.url, request.remote_address, format_exception(err))

    @staticmethod
    def malformed_response(response, client, err):
        return "Malformed response {} for client {}; cause: {}".format(
            response, client, format_exception(err))

    @staticmethod
    def need_policies(req_id):
        return "Policies required but found no policies for request ID: {}".format(req_id)

    @staticmethod
    def policy_service_error(url, req_id, err):
        return "Unable to call policy for {} for request ID: {}; cause: {}".format(
            url, req_id, format_exception(err))

    @staticmethod
    def requesting_url(url, req_id):
        return "Making a call to URL {} for request ID: {}".format(url, req_id)

    @staticmethod
    def requesting(service_name, req_id):
        return "Making a call to service {} for request ID: {}".format(service_name, req_id)

    @staticmethod
    def error_requesting(service_name, req_id, err):
        return "Error while requesting service {} for request ID: {}; cause: {}".format(
            service_name, req_id, format_exception(err))

    @staticmethod
    def calling_back(req_id, callback_url):
        return "Posting result to callback URL for request ID: {}; callback URL={}".format(
            req_id, callback_url)

    @staticmethod
    def calling_back_with_body(req_id, callback_url, body):
        return "Posting result to callback URL for request ID: {}; callback URL={} body={}".format(
            req_id, callback_url, body)

    @staticmethod
    def error_calling_back(req_id, callback_url, err):
        return "Error while posting result to callback URL {} for request ID: {}; cause: {}".format(
            req_id, callback_url, format_exception(err))

    @staticmethod
    def received_request(url, remote_addr, json_body):
        return "Received a call to {} from {} {}".format(url, remote_addr, json_body)

    @staticmethod
    def new_worker_thread(req_id, extra_msg=""):
        res = "Initiating new worker thread for request ID: {}".format(req_id)
        return res + extra_msg

    @staticmethod
    def inside_worker_thread(req_id, extra_msg=""):
        res = "Inside worker thread for request ID: {}".format(req_id)
        return res + extra_msg

    @staticmethod
    def processing(req_id, desc):
        return "Processing request ID: {} -- {}".format(req_id, desc)

    @staticmethod
    def processed(req_id, desc):
        return "Processed request ID: {} -- {}".format(req_id, desc)

    @staticmethod
    def error_while_processing(req_id, desc, err):
        return "Error while processing request ID: {} -- {}; cause: {}".format(
            req_id, desc, format_exception(err))

    @staticmethod
    def creating_local_env(req_id):
        return "Creating local environment request ID: {}".format(
            req_id)

    @staticmethod
    def error_local_env(req_id, desc, err):
        return "Error while creating local environment for request ID: {} -- {}; cause: {}".format(
            req_id, desc, err.__traceback__)

    @staticmethod
    def inside_new_thread(req_id, extra_msg=""):
        res = "Spinning up a new thread for request ID: {}".format(req_id)
        return res + " " + extra_msg

    @staticmethod
    def error_response_posting(req_id, desc, err):
        return "Error while posting a response for a request ID: {} -- {}; cause: {}".format(
            req_id, desc, err.__traceback__)

    @staticmethod
    def received_http_response(resp):
        return "Received response [code: {}, headers: {}, data: {}]".format(
            resp.status_code, resp.headers, resp.__dict__)

    @staticmethod
    def sending_response(req_id, desc):
        return "Response is sent for request ID: {} -- {}".format(
            req_id, desc)

    @staticmethod
    def listening_response(req_id, desc):
        return "Response is sent for request ID: {} -- {}".format(
            req_id, desc)

    @staticmethod
    def items_received(item_num, item_type, desc="Received"):
        return "{} {} {}".format(desc, item_num, item_type)

    @staticmethod
    def items_sent(item_num, item_type, desc="Published"):
        return "{} {} {}".format(desc, item_num, item_type)


MH = OOF_OSDFLogMessageFormatter
error_log, metrics_log, audit_log, debug_log = OOF_OSDFLogMessageHelper().get_handlers()


def warn_audit_error(msg):
    """Log the message to error_log.warn and audit_log.warn"""
    log_message_multi(msg, audit_log.warn, error_log.warn)


def log_message_multi(msg, *logger_methods):
    """Log the msg to multiple loggers
    :param msg: message to log
    :param logger_methods: e.g. error_log.warn, audit_log.warn, etc.
    """
    for log_method in logger_methods:
        log_method(msg)

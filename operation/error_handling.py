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

import json

from schematics.exceptions import DataError

from requests import RequestException
from requests import ConnectionError, HTTPError, Timeout
from osdf.operation.exceptions import BusinessException

import osdf

ERROR_TEMPLATE = osdf.ERROR_TEMPLATE

MESSAGE_BASE = "A solution couldn't be determined because an external application"
HTTP_ERROR_MESSAGE = MESSAGE_BASE + " returned a HTTP error"
TIMEOUT_ERROR_MESSAGE = MESSAGE_BASE + " could not respond in time, please check the external application"
CONNECTION_ERROR_MESSAGE = MESSAGE_BASE + " could not be reached"

internal_error_body = {
        "serviceException": {
            "text": "Unhandled internal exception, request could not be processed"
        }
}

internal_error_message = json.dumps(internal_error_body)


def build_json_error_body(error):
    if isinstance(error,RequestException):
        return request_exception_to_json_body(error)
    elif isinstance(error, DataError):
        return data_error_to_json_body(error)
    elif type(error) is BusinessException: # return the error message, because it is well formatted
        return ERROR_TEMPLATE.render(description=str(error))
    else:
        return internal_error_message


def data_error_to_json_body(error):
        description = str(error).replace('"', '\\"')
        error_message = ERROR_TEMPLATE.render(description=description)
        return error_message


def request_exception_to_json_body(error):
    friendly_message = "A request exception has occurred when contacting an external system"
    if type(error) is HTTPError:
        friendly_message = HTTP_ERROR_MESSAGE
    if type(error) is ConnectionError:
        friendly_message = CONNECTION_ERROR_MESSAGE
    if type(error) is Timeout:
        friendly_message = TIMEOUT_ERROR_MESSAGE

    eie_body = {
            "serviceException": {
                "text": friendly_message,
                "errorType": "InterfaceError"
            },
            "externalApplicationDetails": {
                "httpMethod": error.request.method,
                "url": error.request.url
            }
    }

    response = error.response

    if response is not None:
        eie_body['externalApplicationDetails']['httpStatusCode'] = response.status_code
        content_type = response.headers.get('content-type')
        if content_type is not None:
            if 'application/json' in content_type:
                eie_body['externalApplicationDetails']['responseMessage'] = response.json()
            elif 'text/html' in content_type:
                eie_body['externalApplicationDetails']['responseMessage'] = response.text
    error_message = json.dumps(eie_body)
    return error_message

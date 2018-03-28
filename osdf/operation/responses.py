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

from flask import Response

from osdf import ACCEPTED_MESSAGE_TEMPLATE


def osdf_response_for_request_accept(request_id="", transaction_id="", request_status="", status_message="",
                                     response_code=202, as_http=True):
    """Helper method to create a response object for request acceptance, so that the object can be sent to a client
    :param request_id: request ID provided by the caller
    :param transaction_id: transaction ID provided by the caller
    :param request_status: the status of a request
    :param status_message: details on the status of a request
    :param response_code: the HTTP status code to send -- default is 202 (accepted)
    :param as_http: whether to send response as HTTP response object or as a string
    :return: if as_http is True, return a HTTP Response object. Otherwise, return json-encoded-message
    """
    response_message = ACCEPTED_MESSAGE_TEMPLATE.render(request_id=request_id, transaction_id=transaction_id,
                                                        request_status=request_status, status_message=status_message)
    if not as_http:
        return response_message

    response = Response(response_message, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(response_message))
    response.status_code = response_code
    return response

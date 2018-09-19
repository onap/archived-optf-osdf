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
from osdf.logging.osdf_logging import debug_log

def osdf_response_for_request_accept(request_id="", transaction_id="", request_status="", status_message="",
                                     version_info = {
                                          'placementVersioningEnabled': False,
                                          'placementMajorVersion': '1',
                                          'placementMinorVersion': '0',
                                          'placementPatchVersion': '0'
                                      },
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
    
    placement_ver_enabled = version_info['placementVersioningEnabled']
    
    if placement_ver_enabled:
        placement_minor_version = version_info['placementMinorVersion']
        placement_patch_version = version_info['placementPatchVersion']
        placement_major_version = version_info['placementMajorVersion']
        x_latest_version = placement_major_version+'.'+placement_minor_version+'.'+placement_patch_version
        response.headers.add('X-MinorVersion', placement_minor_version)
        response.headers.add('X-PatchVersion', placement_patch_version)
        response.headers.add('X-LatestVersion', x_latest_version)
        
        debug_log.debug("Versions set in HTTP header for synchronous response: X-MinorVersion: {}  X-PatchVersion: {}  X-LatestVersion: {}"
                        .format(placement_minor_version, placement_patch_version, x_latest_version))
    
    response.status_code = response_code
    return response

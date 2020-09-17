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

import socket
import threading
import time
import uuid

from flask import g
from onaplogging.mdcContext import MDC

EMPTY = "EMPTY"

DATE_FMT = '%Y-%m-%dT%H:%M:%S'


def default_server_info():
    """
    Populate server & server_ip_address MDC fields
    """
    # If not set or purposely set = None, then set default
    if MDC.get('server') is None:
        try:
            server = socket.getfqdn()
        except Exception:
            try:
                server = socket.gethostname()
            except Exception:
                server = ''
        MDC.put('server', server)
    if MDC.get('serverIPAddress') is None:
        try:
            server_ip_address = socket.gethostbyname(MDC.get('server'))
        except Exception:
            server_ip_address = ""
        MDC.put('serverIPAddress', server_ip_address)


def default_mdc():
    """
    Populate default MDC fields
    """
    MDC.put('instanceUUID', generate_uuid())
    MDC.put('InvocationID', generate_uuid())
    MDC.put('serviceName', 'OOF_OSDF')
    MDC.put('threadID', threading.currentThread().getName())
    default_server_info()
    MDC.put('requestID', generate_uuid())
    MDC.put('partnerName', 'N/A')
    MDC.put('entryTimestamp', get_time())


def mdc_from_json(request_json):
    """
    Populate MDC fields given a request in json format
    """
    if MDC.get("instanceUUID") is None:
        default_mdc()
    MDC.put('requestID', get_request_id(request_json))
    MDC.put('partnerName', get_partner_name(request_json))


def populate_default_mdc(request):
    """
    Populate default MDC fields given the request
    """
    if MDC.get("instanceUUID") is None:
        default_mdc()
        g.request_start = time.process_time()
        g.empty_value = "EMPTY"
        g.request_id = MDC.get("requestID")
    MDC.put('serviceName', request.path)
    MDC.put('IPAddress', request.headers.get('X-Forwarded-For', request.remote_addr))


def populate_mdc(request):
    """
    Populate MDC fields from the request headers
    """
    populate_default_mdc(request)
    req_id = request.headers.get('X-ONAP-RequestID', g.empty_value)
    request_json = request.get_json()
    if req_id == g.empty_value:
        req_id = get_request_id(request_json)
    g.request_id = req_id
    MDC.put('requestID', req_id)
    MDC.put('partnerName', get_partner_name(request_json))


def get_request_id(request_json):
    """
    Get the request_id from the request
    """
    request_id = request_json['requestInfo'].get('requestId')
    if not request_id:
        request_id = request_json['requestInfo'].get('requestID')
    return request_id


def generate_uuid():
    """
    Generate an unique uuid
    """
    return f'{uuid.uuid1()}'


def get_partner_name(request_json):
    """
    Get the partnerName
    """
    partner_name = EMPTY
    if 'requestInfo' in request_json:
        partner_name = request_json['requestInfo'].get('sourceId', EMPTY)
    return partner_name


def clear_mdc():
    """
    Clear MDC
    """
    MDC.clear()


def get_time():
    """
    Generate the invocation time string

    The dateformat is %Y-%m-%dT%H:%M:%S.sss
    """
    ct = time.time()
    lt = time.gmtime(ct)
    msec = int((ct - int(ct)) * 1000)
    return f'{time.strftime(DATE_FMT, lt)}.{msec:0>3}'


def set_error_details(code, desc):
    """
    set errorCode and description
    """
    MDC.put('errorCode', code)
    MDC.put('errorDescription', desc)

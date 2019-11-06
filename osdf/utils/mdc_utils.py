# -------------------------------------------------------------------------
#   Copyright (c) 2019 AT&T Intellectual Property
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
import uuid

from onaplogging.mdcContext import MDC


def default_server_info():
    # If not set or purposely set = None, then set default
    if MDC.get('server') is None:
        try:
            server = socket.getfqdn()
        except Exception as err:
            try:
                server = socket.gethostname()
            except Exception as err:
                server = ''
        MDC.put('server', server)
    if MDC.get('serverIPAddress') is None:
        try:
            server_ip_address = socket.gethostbyname(self._fields['server'])
        except Exception:
            server_ip_address = ""
        MDC.put('serverIPAddress', server_ip_address)


def mdc_from_json(request_json):
    MDC.put('instanceUUID', uuid.uuid1())
    MDC.put('serviceName', 'OOF_OSDF')
    MDC.put('threadID', threading.currentThread().getName())
    default_server_info()
    MDC.put('requestID', request_json['requestInfo']['requestId'])
    MDC.put('partnerName', request_json['requestInfo']['sourceId'])


def clear_mdc():
    MDC.clear()

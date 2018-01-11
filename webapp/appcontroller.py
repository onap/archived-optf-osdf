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

from flask import request
from flask_httpauth import HTTPBasicAuth
from flask import Response
import json
import osdf
from osdf.config.base import http_basic_auth_credentials

auth_basic = HTTPBasicAuth()

error_body = {
    "serviceException": {
        "text": "Unauthorized, check username and password"
    }
}

unauthorized_message = json.dumps(error_body)

@auth_basic.get_password
def get_pw(username):
    end_point = request.url.split('/')[-1]
    auth_group = osdf.end_point_auth_mapping.get(end_point)
    return http_basic_auth_credentials[auth_group].get(username) if auth_group else None

@auth_basic.error_handler
def auth_error():
    response = Response(unauthorized_message, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(unauthorized_message))
    response.status_code = 401
    return response

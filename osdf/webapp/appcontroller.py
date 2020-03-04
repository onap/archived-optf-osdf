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
import osdf.config.base as cfg_base
from osdf.config.base import osdf_config
from osdf.adapters.aaf import aaf_authentication as aaf_auth
from osdf.logging.osdf_logging import debug_log

auth_basic = HTTPBasicAuth()

error_body = {
    "serviceException": {
        "text": "Unauthorized, check username and password"
    }
}

unauthorized_message = json.dumps(error_body)


@auth_basic.get_password
def get_pw(username):
    for k in osdf.end_point_auth_mapping:
        if k in request.url:
            auth_group = osdf.end_point_auth_mapping.get(k)
    debug_log.debug(username)
    debug_log.debug(cfg_base.http_basic_auth_credentials[auth_group])
    return cfg_base.http_basic_auth_credentials[auth_group].get(username) if auth_group else None


@auth_basic.error_handler
def auth_error():
    response = Response(unauthorized_message, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(unauthorized_message))
    response.status_code = 401
    return response


@auth_basic.verify_password
def verify_pw(username, password):
    is_aaf_enabled = osdf_config.deployment.get('is_aaf_enabled', False)
    if is_aaf_enabled:
        return aaf_auth.authenticate(username, password)
    else:
        pw = get_pw(username)
        return pw == password

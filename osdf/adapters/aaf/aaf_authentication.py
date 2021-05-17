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

import base64
from datetime import datetime
from datetime import timedelta
from flask import request
import re

from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import debug_log
from osdf.logging.osdf_logging import error_log
from osdf.utils.interfaces import RestClient

AUTHZ_PERMS_USER = '{}/authz/perms/user/{}'

EXPIRE_TIME = 'expire_time'

perm_cache = {}
deploy_config = osdf_config.deployment


def clear_cache():
    perm_cache.clear()


def authenticate(uid, passwd):
    try:
        perms = get_aaf_permissions(uid, passwd)
        return has_valid_role(perms)
    except Exception as exp:
        error_log.error("Error Authenticating the user {} : {}: ".format(uid, exp))
    return False


"""
Check whether the user has valid permissions
return True if the user has valid permissions
else return false
"""


def has_valid_role(perms):
    aaf_user_roles = deploy_config['aaf_user_roles']

    aaf_roles = get_role_list(perms)

    for roles in aaf_user_roles:
        path_perm = roles.split(':')
        uri = path_perm[0]
        perm = path_perm[1].split('|')
        p = (perm[0], perm[1], perm[2].split()[0])
        if re.search(uri, request.path) and p in aaf_roles:
            return True
    return False


"""
Build a list of roles tuples from the AAF response.

"""


def get_role_list(perms):
    role_list = []
    if perms:
        roles = perms.get('roles')
        if roles:
            perm = roles.get('perm', [])
            for p in perm:
                role_list.append((p['type'], p['instance'], p['action']))
    return role_list


def get_aaf_permissions(uid, passwd):
    key = base64.b64encode(bytes("{}_{}".format(uid, passwd), "ascii"))
    time_delta = timedelta(minutes=deploy_config.get('aaf_cache_expiry_mins', 5))

    perms = perm_cache.get(key)

    if perms and datetime.now() < perms.get(EXPIRE_TIME):
        debug_log.debug("Returning cached value")
        return perms
    debug_log.debug("Invoking AAF authentication API")
    perms = {EXPIRE_TIME: datetime.now() + time_delta, 'roles': remote_api(passwd, uid)}
    perm_cache[key] = perms
    return perms


def remote_api(passwd, uid):
    headers = {"Accept": "application/Users+xml;q=1.0;charset=utf-8;version=2.0,text/xml;q=1.0;version=2.0"}
    url = AUTHZ_PERMS_USER.format(deploy_config['aaf_url'], uid)
    rc = RestClient(userid=uid, passwd=passwd, headers=headers, url=url, log_func=debug_log.debug,
                    req_id='aaf_user_id')
    return rc.request(method='GET', asjson=True)

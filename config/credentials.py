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

from osdf import auth_groups, userid_suffix, passwd_suffix


def dmaap_creds(dmaap_file="/etc/dcae/dmaap.conf"):
    """Get DMaaP credentials from DCAE for publish and subscribe"""
    try:
        dmaap_creds = _get_dmaap_creds(dmaap_file)
    except:
        dmaap_creds = {}
    return dmaap_creds


def _get_dmaap_creds(dmaap_file):
    """Get DMaaP credentials from DCAE for publish and subscribe"""
    streams = json.load(open(dmaap_file, 'r'))
    pubs = [x for x in streams
            if x['dmaapStreamId'] == 'requests' and x['dmaapAction'] == 'publish']
    subs = [x for x in streams
            if x['dmaapStreamId'] == 'responses' and x['dmaapAction'] == 'subscribe']

    def get_dmaap_info(x):
        """Get DMaaP credentials from dmaap_object 'x'"""
        return dict(url=x.get('dmaapUrl'), userid=x.get('dmaapUserName'), passwd=x.get('dmaapPassword'))

    return {'pub': get_dmaap_info(pubs[0]), 'sub': get_dmaap_info(subs[0])}


def load_credentials(osdf_config):
    """Get credentials as dictionaries grouped by auth_group (e.g. creds["Placement"]["user1"] = "pass1")"""
    creds = dict((x, dict()) for x in auth_groups)  # each auth group has userid, passwd dict
    suffix_start = len(userid_suffix)

    config = osdf_config.deployment

    for element, username in config.items():
        for x in auth_groups:
            if element.startswith("osdf" + x) and element.endswith(userid_suffix):
                passwd = config[element[:-suffix_start] + passwd_suffix]
                creds[x][username] = passwd
    return creds

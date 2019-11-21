# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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

from datetime import datetime as dt

from osdf.logging.osdf_logging import debug_log
from osdf.utils.interfaces import RestClient


def request_ns(req_object, osdf_config, flat_policies, req_type):
    """
    Process a configdb request from a Client (build Conductor API call, make the call, return result)
    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :param flat_policies: policies related to PCI Opt (fetched based on request)
    :return: response from ConfigDB (accounting for redirects from Conductor service
    """

    ns_remote_resp = ""
    config = osdf_config.deployment
    local_config = osdf_config.core
    uid, passwd = config['nsconfigDbUserName'], config['nsconfigDbPassword']
    req_id = req_object['requestInfo']['requestId']
    transaction_id = req_object['requestInfo']['transactionId']
    headers = dict(transaction_id=transaction_id)

    rc = RestClient(userid=uid, passwd=passwd, method="GET", log_func=debug_log.debug, headers=headers)

    nsconfig_url = get_nsconfigdb_url(req_object, config, req_type)

    # if url not empty then fire rest call
    if nsconfig_url.strip():
        ns_remotecall_resp = rc.request(raw_response=True, url=nsconfig_url)
        # if response not empty
        if ns_remotecall_resp.text:
            ns_remote_resp = ns_remotecall_resp.json()

    return ns_remote_resp


def get_nsconfigdb_url(req_object, config, req_type):
    ts = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S%z')
    if req_type == "NSI":
        nst_uuid = req_object['NSTInfo']['UUID']
        nsconfigdb_url = '{}/{}/{}/{}'.format(config['nsconfigDbUrl'], config['nsconfigDbNSIUrl'], nst_uuid, ts)

    elif req_type == "NSSI":
        nsst_uuid = req_object['NSSTInfo']['UUID']
        nsconfigdb_url = '{}/{}/{}/{}'.format(config['nsconfigDbUrl'], config['nsconfigDbNSSIUrl'], nsst_uuid, ts)
    elif req_type == "NST":
        latency_id = req_object['serviceProfile']['latency']
        nsconfigdb_url = '{}/{}/{}/{}'.format(config['nsconfigDbUrl'], config['nsconfigDbNSTUrl'], latency_id, ts)
    else:
        nsconfigdb_url = ""

    return nsconfigdb_url

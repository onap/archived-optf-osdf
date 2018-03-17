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
import itertools
import json


from requests import RequestException
from osdf.operation.exceptions import BusinessException
from osdf.adapters.local_data.local_policies import get_local_policies
from osdf.adapters.policy.utils import _regex_policy_name
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import audit_log, MH, metrics_log, error_log, debug_log
from osdf.utils.interfaces import RestClient
from osdf.optimizers.placementopt.conductor.api_builder import retrieve_node
# from osdf.utils import data_mapping


def get_by_name(rest_client, policy_name_list, wildcards=True):
    policy_list = []
    for policy_name in policy_name_list:
        try:
            query_name = policy_name
            if wildcards:
                query_name = _regex_policy_name(query_name)
            policy_list.append(rest_client.request(json={"policyName": query_name}))
        except RequestException as err:
            audit_log.warn("Error in fetching policy: " + policy_name)
            raise BusinessException("Cannot fetch policy {}: ".format(policy_name), err)
    return policy_list


def get_subscriber_name(req, pmain):
    subs_name = retrieve_node(req, pmain['subscriber_name'])
    if subs_name is None:
        return "DEFAULT"
    else:
        subs_name_uc = subs_name.upper()
        if subs_name_uc in ("DEFAULT", "NULL", ""):
            subs_name = "DEFAULT"
    return subs_name


def get_subscriber_role(rest_client, req, pmain, service_name, scope):
    """Make a request to policy and return subscriberRole
    :param rest_client: rest client to make call
    :param req: request object from MSO
    :param pmain: main config that will have policy path information
    :param service_name: the type of service to call: e.g. "vCPE
    :param scope: the scope of policy to call: e.g. "OOF_HAS_vCPE".
    :return: subscriberRole and provStatus retrieved from Subscriber policy
    """
    subscriber_role = "DEFAULT"
    prov_status = []
    subs_name = get_subscriber_name(req, pmain)
    if subs_name == "DEFAULT":
        return subscriber_role, prov_status
    
    policy_subs = pmain['policy_subscriber']
    policy_scope = {"policyName": "{}.*".format(scope),
                    "configAttributes": {
                        "serviceType": "{}".format(service_name),
                        "service": "{}".format(policy_subs)}
                    }
    policy_list = []
    try:
        policy_list.append(rest_client.request(json=policy_scope))
    except RequestException as err:
        audit_log.warn("Error in fetching policy for {}: ".format(policy_subs))
        return subscriber_role, prov_status
            
    formatted_policies = []
    for x in itertools.chain(*policy_list):
        if x['config'] is None:
            raise BusinessException("Config not found for policy with name %s" % x['policyName'])
        else:
            formatted_policies.append(json.loads(x['config']))
    
    for policy in formatted_policies:
        property_list = policy['content']['property']
        for prop in property_list:
            if subs_name in prop['subscriberName']:
                subs_role_list = prop['subscriberRole']
                prov_status = prop['provStatus']
                if isinstance(subs_role_list, list): # as list is returned
                    return subs_role_list[0], prov_status
    return subscriber_role, prov_status
    

def get_by_scope(rest_client, req, config_local, type_service):
    policy_list = []
    pmain = config_local['policy_info'][type_service]
    pscope = pmain['policy_scope']
    
    model_name = retrieve_node(req, pscope['service_name'])
    service_name = model_name

    scope = pscope['scope_{}'.format(service_name.lower())]
    subscriber_role, prov_status = get_subscriber_role(rest_client, req, pmain, service_name, scope)
    policy_type_list = pmain['policy_type_{}'.format(service_name.lower())]
    for policy_type in policy_type_list:
        policy_scope = {"policyName": "{}.*".format(scope),
                        "configAttributes": {
                            "serviceType": "{}".format(service_name),
                            "service": "{}".format(policy_type),
                            "subscriberRole": "{}".format(subscriber_role)}
                        }
        policy_list.append(rest_client.request(json=policy_scope))
    return policy_list, prov_status


def remote_api(req_json, osdf_config, service_type="placement"):
    """Make a request to policy and return response -- it accounts for multiple requests that be needed
    :param req_json: policy request object (can have multiple policy names)
    :param osdf_config: main config that will have credential information
    :param service_type: the type of service to call: "placement", "scheduling"
    :return: all related policies and provStatus retrieved from Subscriber policy
    """
    prov_status = None
    config = osdf_config.deployment
    uid, passwd = config['policyPlatformUsername'], config['policyPlatformPassword']
    pcuid, pcpasswd = config['policyClientUsername'], config['policyClientPassword']
    headers = {"ClientAuth": base64.b64encode(bytes("{}:{}".format(pcuid, pcpasswd), "ascii"))}
    headers.update({'Environment': config['policyPlatformEnv']})
    url = config['policyPlatformUrl']
    rc = RestClient(userid=uid, passwd=passwd, headers=headers, url=url, log_func=debug_log.debug)

    if osdf_config.core['policy_info'][service_type]['policy_fetch'] == "by_name":
        policies = get_by_name(rc, req_json[service_type + "Info"]['policyId'], wildcards=True)
    elif osdf_config.core['policy_info'][service_type]['policy_fetch'] == "by_name_no_wildcards":
        policies = get_by_name(rc, req_json[service_type + "Info"]['policyId'], wildcards=False)
    else:  # Get policy by scope
        policies, prov_status = get_by_scope(rc, req_json, osdf_config.core, service_type)

    # policies in res are list of lists, so flatten them; also only keep config part
    formatted_policies = []
    for x in itertools.chain(*policies):
        if x['config'] is None:
            raise BusinessException("Config not found for policy with name %s" % x['policyName'])
        else:
            formatted_policies.append(json.loads(x['config']))
    return formatted_policies, prov_status


def local_policies_location(req_json, osdf_config, service_type):
    """
    Get folder and list of policy_files if "local policies" option is enabled
    :param service_type: placement supported for now, but can be any other service
    :return: a tuple (folder, file_list) or None
    """
    lp = osdf_config.core.get('osdf_temp', {}).get('local_policies', {})
    if lp.get('global_disabled'):
        return None  # short-circuit to disable all local policies
    if lp.get('local_{}_policies_enabled'.format(service_type)):
        if service_type == "scheduling":
            return lp.get('{}_policy_dir'.format(service_type)), lp.get('{}_policy_files'.format(service_type))
        else:
            required_node = osdf_config.core['policy_info'][service_type]['policy_scope']['service_name']
            model_name = retrieve_node(req_json, required_node)
            service_name = model_name  # TODO: data_mapping.get_service_type(model_name)
            return lp.get('{}_policy_dir_{}'.format(service_type, service_name.lower())), \
                   lp.get('{}_policy_files_{}'.format(service_type, service_name.lower()))
    return None


def get_policies(request_json, service_type):
    """Validate the request and get relevant policies
    :param request_json: Request object
    :param service_type: the type of service to call: "placement", "scheduling"
    :return: policies associated with this request and provStatus retrieved from Subscriber policy
    """
    prov_status = []
    req_info = request_json['requestInfo']
    req_id = req_info['requestId']
    metrics_log.info(MH.requesting("policy", req_id))
    local_info = local_policies_location(request_json, osdf_config, service_type)

    if local_info:  # tuple containing location and list of files
        to_filter = None
        if osdf_config.core['policy_info'][service_type]['policy_fetch'] == "by_name":
            to_filter = request_json[service_type + "Info"]['policyId']
        policies = get_local_policies(local_info[0], local_info[1], to_filter)
    else:
        policies, prov_status = remote_api(request_json, osdf_config, service_type)
        
    return policies, prov_status

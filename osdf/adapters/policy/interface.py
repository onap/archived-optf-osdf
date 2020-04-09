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
import yaml
import os
import uuid


from requests import RequestException
from osdf.operation.exceptions import BusinessException
from osdf.adapters.local_data.local_policies import get_local_policies
from osdf.adapters.policy.utils import policy_name_as_regex, retrieve_node
from osdf.utils.programming_utils import list_flatten, dot_notation
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import audit_log, MH, metrics_log, debug_log
from osdf.utils.interfaces import RestClient


def get_by_name(rest_client, policy_name_list, wildcards=True):
    policy_list = []
    for policy_name in policy_name_list:
        try:
            query_name = policy_name
            if wildcards:
                query_name = policy_name_as_regex(query_name)
            policy_list.append(rest_client.request(json={"policyName": query_name}))
        except RequestException as err:
            audit_log.warn("Error in fetching policy: " + policy_name)
            raise BusinessException("Cannot fetch policy {}: ".format(policy_name), err)
    return policy_list


def get_by_scope(rest_client, req, config_local, type_service):
    """ Get policies by scopes as defined in the configuration file.
    :param rest_client: a rest client object to make a call.
    :param req: an optimization request.
    :param config_local: application configuration file.
    :param type_service: the type of optimization service.
    :return: policies in the form of list of list where inner list contains policies for a single a scope.
    """
    scope_policies = []
    references = config_local.get('references', {})
    pscope = config_local.get('policy_info', {}).get(type_service, {}).get('policy_scope', [])
    scope_fields = {}
    policies = {}
    for scopes in pscope:
        for key in scopes.keys():
            for field in scopes[key]:
                scope_fields[key] = list_flatten([get_scope_fields(field, references, req, policies)
                                                      if 'get_param' in field else field])
        if scope_fields.get('resources') and len(scope_fields['resources']) > 1:
            for s in scope_fields['resources']:
                scope_fields['resources'] = [s]
                policies.update(policy_api_call(rest_client, scope_fields).get('policies', {}))
        else:
            policies.update(policy_api_call(rest_client, scope_fields).get('policies', {}))
        for policyName in policies.keys():
            keys = scope_fields.keys() & policies[policyName]['properties'].keys()
            policy = {}
            policy[policyName] = policies[policyName]
            scope_policies.append(policy for k in keys
                                  if set(policies.get(policyName, {}).get('properties',{}).get(k)) >= set(scope_fields[k])
                                  and policy not in scope_policies)

    return scope_policies


def get_scope_fields(field, references, req, policies):
    """ Retrieve the values for scope fields from a request and policies as per the configuration
    and references defined in a configuration file. If the value of a scope field missing in a request or
    policies, throw an exception since correct policies cannot be retrieved.
    :param field: details on a scope field from a configuration file.
    :param references: references defined in a configuration file.
    :param req: an optimization request.
    :param policy_info: a list of policies.
    :return: scope fields retrieved from a request and policies.
    """
    ref_source = references.get(field.get('get_param', ""), {}).get('source')
    ref_value = references.get(field.get('get_param', ""), {}).get('value')
    if ref_source == "request":
        scope_field = dot_notation(req, ref_value)
        if scope_field:
            return scope_field
        raise BusinessException("Field {} is missing a value in a request".format(ref_value.split('.')[-1]))
    else:
        scope_fields = []
        for policyName in policies.keys():
            policy_content = policies.get(policyName)
            if policy_content.get('type', "invalid_policy") == ref_source:
                scope_fields.append(dot_notation(policy_content, ref_value))
        scope_values = list_flatten(scope_fields)
        if len(scope_values) > 0:
            return scope_values
        raise BusinessException("Field {} is missing a value in all policies of type {}".format(
            ref_value.split('.')[-1], ref_source))

def policy_api_call(rest_client, scope_fields):
    """
    :param rest_client: rest client to make a call
    :param scope_fields: a collection of scopes to be used for filtering
    :return: a list of policies matching all filters
    """
    api_call_body = {"ONAPName": "OOF",
                     "ONAPComponent": "OOF_Component",
                     "ONAPInstance": "OOF_Component_Instance",
                     "action": "optimize",
                     "resources": scope_fields}
    return rest_client.request(json=api_call_body)

def remote_api(req_json, osdf_config, service_type="placement"):
    """Make a request to policy and return response -- it accounts for multiple requests that be needed
    :param req_json: policy request object (can have multiple policy names)
    :param osdf_config: main config that will have credential information
    :param service_type: the type of service to call: "placement", "scheduling"
    :return: all related policies and provStatus retrieved from Subscriber policy
    """
    config = osdf_config.deployment
    headers = {"Content-type: application/json"}
    uid, passwd = config['policyPlatformUsername'], config['policyPlatformPassword']
    url = config['policyPlatformUrl']
    rc = RestClient(userid=uid, passwd=passwd, headers=headers, url=url, log_func=debug_log.debug)

    if osdf_config.core['policy_info'][service_type]['policy_fetch'] == "by_name":
        policies = get_by_name(rc, req_json[service_type + "Info"]['policyId'], wildcards=True)
    elif osdf_config.core['policy_info'][service_type]['policy_fetch'] == "by_name_no_wildcards":
        policies = get_by_name(rc, req_json[service_type + "Info"]['policyId'], wildcards=False)
    else:
        policies = get_by_scope(rc, req_json, osdf_config.core, service_type)

    formatted_policies = []
    for x in itertools.chain(*policies):
        if x[list(x.keys())[0]].get('properties') is None:
            raise BusinessException("Properties not found for policy with name %s" % x[list(x.keys()[0])])
        else:
            formatted_policies.append(x)
    return formatted_policies


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
        debug_log.debug('Loading local policies for service type: {}'.format(service_type))
        if service_type == "scheduling":
            return lp.get('{}_policy_dir'.format(service_type)), lp.get('{}_policy_files'.format(service_type))
        else:
            service_name = req_json['serviceInfo']['serviceName']  # TODO: data_mapping.get_service_type(model_name)
            debug_log.debug('Loading local policies for service name: {}'.format(service_name))
            return lp.get('{}_policy_dir_{}'.format(service_type, service_name.lower())), \
                   lp.get('{}_policy_files_{}'.format(service_type, service_name.lower()))
    return None


def get_policies(request_json, service_type):
    """Validate the request and get relevant policies
    :param request_json: Request object
    :param service_type: the type of service to call: "placement", "scheduling"
    :return: policies associated with this request and provStatus retrieved from Subscriber policy
    """
    req_info = request_json['requestInfo']
    req_id = req_info['requestId']
    metrics_log.info(MH.requesting("policy", req_id))
    local_info = local_policies_location(request_json, osdf_config, service_type)

    if local_info:  # tuple containing location and list of files
        if local_info[0] is None or local_info[1] is None:
            raise ValueError("Error fetching local policy info")
        to_filter = None
        if osdf_config.core['policy_info'][service_type]['policy_fetch'] == "by_name":
            to_filter = request_json[service_type + "Info"]['policyId']
        policies = get_local_policies(local_info[0], local_info[1], to_filter)
    else:
        policies = remote_api(request_json, osdf_config, service_type)

    return policies

def upload_policy_models():
    """Upload all the policy models reside in the folder"""
    requestId = uuid.uuid4()
    config = osdf_config.deployment
    model_path = config['pathPolicyModelUpload']
    uid, passwd = config['policyPlatformUsername'], config['policyPlatformPassword']
    pcuid, pcpasswd = config['policyClientUsername'], config['policyClientPassword']
    headers = {"ClientAuth": base64.b64encode(bytes("{}:{}".format(pcuid, pcpasswd), "ascii"))}
    headers.update({'Environment': config['policyPlatformEnv']})
    headers.update({'X-ONAP-RequestID': requestId})
    url = config['policyPlatformUrlModelUpload']
    rc = RestClient(userid=uid, passwd=passwd, headers=headers, url=url, log_func=debug_log.debug)

    for file in os.listdir(model_path):
        if not file.endswith(".yaml"):
            continue
        with open(file) as f:
            file_converted = json.dumps(yaml.load(f))
            response = rc.request(json=file_converted, ok_codes=(200))
        if not response:
            success = False
            audit_log.warn("Policy model %s uploading failed!" % file)
    if not success:
        return "Policy model uploading success!"
    else:
        return "Policy model uploading not success!"

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

import copy
import json
from jinja2 import Template
from osdf.utils.programming_utils import list_flatten, dot_notation
import osdf.optimizers.placementopt.conductor.translation as tr
from osdf.adapters.policy.utils import group_policies


def conductor_api_builder(request_json, flat_policies: list, local_config, prov_status,
                          template="templates/conductor_interface.json"):
    """Build a SNIRO southbound API call for Conductor/Placement optimization
    :param request_json: parameter data received from a client
    :param flat_policies: policy data received from the policy platform (flat policies)
    :param template: template to generate southbound API call to conductor
    :param local_config: local configuration file with pointers for the service specific information
    :param prov_status: provStatus retrieved from Subscriber policy
    :return: json to be sent to Conductor/placement optimization
    """
    templ = Template(open(template).read())
    gp = group_policies(flat_policies)
    demand_vnf_name_list = []

    for placementDemand in request_json['placementInfo']['placementDemands']:
        demand_vnf_name_list.append(placementDemand['resourceModuleName'])

    demand_list = tr.gen_demands(request_json, gp['vnfPolicy'])
    attribute_policy_list = tr.gen_attribute_policy(demand_vnf_name_list, gp['attribute'])
    distance_to_location_policy_list = tr.gen_distance_to_location_policy(
        demand_vnf_name_list, gp['distance_to_location'])
    inventory_policy_list = tr.gen_inventory_group_policy(demand_vnf_name_list, gp['inventory_group'])
    resource_instance_policy_list = tr.gen_resource_instance_policy(
        demand_vnf_name_list, gp['instance_fit'])
    resource_region_policy_list = tr.gen_resource_region_policy(demand_vnf_name_list, gp['region_fit'])
    zone_policy_list = tr.gen_zone_policy(demand_vnf_name_list, gp['zone'])
    optimization_policy_list = tr.gen_optimization_policy(demand_vnf_name_list, gp['placementOptimization'])
    reservation_policy_list = tr.gen_reservation_policy(demand_vnf_name_list, gp['instance_reservation'])
    conductor_policies = [attribute_policy_list, distance_to_location_policy_list, inventory_policy_list,
                          resource_instance_policy_list, resource_region_policy_list, zone_policy_list]
    filtered_policies = [x for x in conductor_policies if len(x) > 0]
    policy_groups = list_flatten(filtered_policies)
    reservation_policies = [x for x in reservation_policy_list if len(x) > 0]
    reservation_groups = list_flatten(reservation_policies)
    req_info = request_json['requestInfo']
    model_name = request_json['serviceInfo']['serviceName']
    service_type = model_name
    # service_type = data_mapping.get_service_type(model_name)
    service_info = local_config.get('service_info', {}).get(service_type, {})
    order_info = {}
    if 'orderInfo' in request_json["placementInfo"]:
        order_info = json.loads(request_json["placementInfo"]["orderInfo"])
    request_type = req_info.get('requestType', None)
    subs_com_site_id = ""
    if 'subscriberInfo' in request_json['placementInfo']: 
        subs_com_site_id = request_json['placementInfo']['subscriberInfo'].get('subscriberCommonSiteId', "")
    rendered_req = None
    if service_type == 'vCPE':
        # data_mapping.normalize_user_params(order_info)
        rendered_req = templ.render(
            requestType=request_type,
            chosenComplex=subs_com_site_id,
            demand_list=demand_list,
            policy_groups=policy_groups,
            optimization_policies=optimization_policy_list,
            name=req_info['requestId'],
            timeout=req_info['timeout'],
            limit=req_info['numSolutions'],
            serviceType=service_type,
            serviceInstance=request_json['serviceInfo']['serviceInstanceId'],
            provStatus = prov_status,
            chosenRegion=order_info.get('requestParameters',{}).get('lcpCloudRegionId'),
            json=json)
    json_payload = json.dumps(json.loads(rendered_req)) # need this because template's JSON is ugly!
    return json_payload


def retrieve_node(req_json, reference):
    """
    Get the child node(s) from the dot-notation [reference] and parent [req_json].
    For placement and other requests, there are encoded JSONs inside the request or policy,
    so we need to expand it and then do a search over the parent plus expanded JSON.
    """
    req_json_copy = copy.deepcopy(req_json)  # since we expand the JSON in place, we work on a copy
    if 'orderInfo' in req_json_copy['placementInfo']:
        req_json_copy['placementInfo']['orderInfo'] = json.loads(req_json_copy['placementInfo']['orderInfo'])
    info = dot_notation(req_json_copy, reference)
    return list_flatten(info) if isinstance(info, list) else info


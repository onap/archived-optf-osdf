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

from jinja2 import Template

import osdf.optimizers.placementopt.conductor.translation as tr
from osdf.adapters.policy.utils import group_policies_gen
from osdf.utils.programming_utils import list_flatten


def conductor_api_builder(request_json, flat_policies: list, local_config,
                          template="osdf/templates/conductor_interface.json"):
    """Build an OSDF southbound API call for HAS-Conductor/Placement optimization
    :param request_json: parameter data received from a client
    :param flat_policies: policy data received from the policy platform (flat policies)
    :param template: template to generate southbound API call to conductor
    :param local_config: local configuration file with pointers for the service specific information
    :param prov_status: provStatus retrieved from Subscriber policy
    :return: json to be sent to Conductor/placement optimization
    """
    templ = Template(open(template).read())
    gp = group_policies_gen(flat_policies, local_config)
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
    capacity_policy_list = tr.gen_capacity_policy(demand_vnf_name_list, gp['vim_fit'])
    hpa_policy_list = tr.gen_hpa_policy(demand_vnf_name_list, gp['hpa'])
    req_params_dict = tr.get_opt_query_data(request_json, gp['optimizationQueryPolicy'])
    conductor_policies = [attribute_policy_list, distance_to_location_policy_list, inventory_policy_list,
                          resource_instance_policy_list, resource_region_policy_list, zone_policy_list,
                          reservation_policy_list, capacity_policy_list, hpa_policy_list]
    filtered_policies = [x for x in conductor_policies if len(x) > 0]
    policy_groups = list_flatten(filtered_policies)
    req_info = request_json['requestInfo']
    request_type = req_info.get('requestType', None)
    rendered_req = templ.render(
        requestType=request_type,
        demand_list=demand_list,
        policy_groups=policy_groups,
        optimization_policies=optimization_policy_list,
        name=req_info['requestId'],
        timeout=req_info['timeout'],
        limit=req_info['numSolutions'],
        service_type=request_json['serviceInfo']['serviceName'],
        service_id=request_json['serviceInfo']['serviceInstanceId'],
        latitude=req_params_dict.get("customerLatitude", 0.0),
        longitude=req_params_dict.get("customerLongitude", 0.0),
        json=json)
    json_payload = json.dumps(json.loads(rendered_req))  # need this because template's JSON is ugly!
    return json_payload

# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
#   Copyright (C) 2020 Wipro Limited.
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

from jinja2 import Template
import json

from osdf.adapters.policy.utils import group_policies_gen
import osdf.adapters.conductor.translation as tr
from osdf.utils.programming_utils import list_flatten


def _build_parameters(group_policies, service_info, request_parameters):
    """
        Function prepares parameters section for has request
        :param group_policies: filtered policies
        :param service_info: service info
        :param request_parameters: request parameters
        :return:
        """
    initial_params = tr.get_opt_query_data(request_parameters, group_policies['onap.policies.optimization.QueryPolicy'])
    params = dict()
    params.update({"REQUIRED_MEM": initial_params.pop("requiredMemory", "")})
    params.update({"REQUIRED_DISK": initial_params.pop("requiredDisk", "")})
    params.update({"customer_lat": initial_params.pop("customerLatitude", 0.0)})
    params.update({"customer_long": initial_params.pop("customerLongitude", 0.0)})
    params.update({"service_name": service_info.get('serviceName', "")})
    params.update({"service_id": service_info.get('serviceInstanceId', "")})

    for key, val in initial_params.items():
        if val and val != "":
            params.update({key: val})

    return params


def conductor_api_builder(req_info, demands, request_parameters, service_info, flat_policies: list, local_config,
                          template="osdf/adapters/conductor/templates/conductor_interface.json"):
    """Build an OSDF southbound API call for HAS-Conductor/Placement optimization
        :param req_info: parameter data received from a client
        :param demands: list of demands
        :param request_parameters: request parameters
        :param service_info: service info object
        :param flat_policies: policy data received from the policy platform (flat policies)
        :param template: template to generate southbound API call to conductor
        :param local_config: local configuration file with pointers for the service specific information
        :return: json to be sent to Conductor/placement optimization
        """

    templ = Template(open(template).read())
    gp = group_policies_gen(flat_policies, local_config)
    demand_name_list = []
    for demand in demands:
        demand_name_list.append(demand['resourceModuleName'].lower())
    demand_list = tr.gen_demands(demands, gp['onap.policies.optimization.VnfPolicy'])
    # What's the attribute policy? Need an example
    attribute_policy_list = tr.gen_attribute_policy(demand_name_list, gp['attribute'])
    distance_to_location_policy_list = tr.gen_distance_to_location_policy(
        demand_name_list, gp['onap.policies.optimization.DistancePolicy'])
    # What's the inventory group policy? A policy to choose the inventory group from existing list?
    inventory_policy_list = tr.gen_inventory_group_policy(demand_name_list, gp['inventory_group'])
    # What's the instance fit policy, a policy to choose the instance from existing list?
    resource_instance_policy_list = tr.gen_resource_instance_policy(
        demand_name_list, gp['instance_fit'])
    # Need an example for the resource_region_policy
    resource_region_policy_list = tr.gen_resource_region_policy(demand_name_list, gp['region_fit'])
    zone_policy_list = tr.gen_zone_policy(demand_name_list, gp['onap.policies.optimization.AffinityPolicy'])
    optimization_policy_list = tr.gen_optimization_policy(demand_name_list,
                                                          gp['onap.policies.optimization.OptimizationPolicy'])
    # Need an example for the instance reservation policy
    reservation_policy_list = tr.gen_reservation_policy(demand_name_list, gp['instance_reservation'])
    capacity_policy_list = tr.gen_capacity_policy(demand_name_list, gp['onap.policies.optimization.Vim_fit'])
    hpa_policy_list = tr.gen_hpa_policy(demand_name_list, gp['onap.policies.optimization.HpaPolicy'])
    #distance_to_location_policy_list = tr.gen_distance_to_location_policy(
    #    demand_vnf_name_list, gp['distance_to_location'])
    # demand_list = tr.gen_demands(request_json, gp['vnfPolicy'])
    #zone_policy_list = tr.gen_zone_policy(demand_vnf_name_list, gp['zone'])
    #optimization_policy_list = tr.gen_optimization_policy(demand_vnf_name_list, gp['placement_optimization'])
    #capacity_policy_list = tr.gen_capacity_policy(demand_vnf_name_list, gp['vim_fit'])
    #hpa_policy_list = tr.gen_hpa_policy(demand_vnf_name_list, gp['hpa'])
    req_params_dict = _build_parameters(gp, service_info, request_parameters)
    conductor_policies = [attribute_policy_list, distance_to_location_policy_list, inventory_policy_list,
                          resource_instance_policy_list, resource_region_policy_list, zone_policy_list,
                          reservation_policy_list, capacity_policy_list, hpa_policy_list]
    filtered_policies = [x for x in conductor_policies if len(x) > 0]
    policy_groups = list_flatten(filtered_policies)
    request_type = req_info.get('requestType', None)
    rendered_req = templ.render(
        requestType=request_type,
        demand_list=demand_list,
        policy_groups=policy_groups,
        optimization_policies=optimization_policy_list,
        name=req_info['requestId'],
        timeout=req_info['timeout'],
        limit=req_info['numSolutions'],
        request_params=req_params_dict,
        json=json)
    json_payload = json.dumps(json.loads(rendered_req))  # need this because template's JSON is ugly!
    return json_payload

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
from osdf.utils.data_conversion import text_to_symbol
# from osdf.utils import data_mapping

def gen_optimization_policy(vnf_list, optimization_policy):
    """Generate optimization policy details to pass to Conductor
    :param vnf_list: List of vnf's to used in placement request
    :param optimization_policy: optimization policy information provided in the incoming request
    :return: List of optimization policies in a format required by Conductor
    """
    optimization_policy_list = []
    for policy in optimization_policy:
        content = policy['content']
        parameter_list = []

        for attr in content['objectiveParameter']['parameterAttributes']:
            parameter = attr['parameter'] if attr['parameter'] == "cloud_version" else attr['parameter']+"_between"
            for res in attr['resource']:
                vnf = get_matching_vnf(res, vnf_list)
                value = [vnf] if attr['parameter'] == "cloud_version" else [attr['customerLocationInfo'], vnf]
                parameter_list.append({
                    attr['operator']: [attr['weight'], {parameter: value}]
                })

        optimization_policy_list.append({
                content['objective']: {content['objectiveParameter']['operator']: parameter_list }
        })
    return optimization_policy_list


def get_matching_vnf(resource, vnf_list):
    
    for vnf in vnf_list:
        if resource in vnf:
            return vnf
    return resource


def get_matching_vnfs(resources, vnf_list, match_type="intersection"):
    """Get a list of matching VNFs from the list of resources
    :param resources:
    :param vnf_list: List of vnf's to used in placement request
    :param match_type: "intersection" or "all" or "any" (any => send all_vnfs if there is any intersection)
    :return: List of matching VNFs
    """
    common_vnfs = []
    for vnf in vnf_list:
        for resource in resources:
            if resource in vnf:
                common_vnfs.append(vnf)
    if match_type == "intersection":  # specifically requested intersection
        return common_vnfs
    elif common_vnfs or match_type == "all":  # ("any" and common) OR "all"
        return resources
    return None


def gen_policy_instance(vnf_list, resource_policy, match_type="intersection", rtype=None):
    """Generate a list of policies
    :param vnf_list: List of vnf's to used in placement request
    :param resource_policy: policy for this specific resource
    :param match_type: How to match the vnf_names with the vnf_list (intersection or "any")
             intersection => return intersection; "any" implies return all vnf_names if intersection is not null
    :param rtype: resource type (e.g. resourceRegionProperty or resourceInstanceProperty)
             None => no controller information added to the policy specification to Conductor
    :return: resource policy list in a format required by Conductor
    """
    resource_policy_list = []
    related_policies = []
    for policy in resource_policy:
        pc = policy['content']
        demands = get_matching_vnfs(pc['resourceInstanceType'], vnf_list, match_type=match_type)
        resource = {pc['identity']: {'type': pc['type'], 'demands': demands}}

        if rtype:
            resource[pc['identity']]['properties'] = {'controller': pc[rtype]['controller'],
                                                      'request': json.loads(pc[rtype]['request'])}
        if demands and len(demands) != 0:
            resource_policy_list.append(resource)
            related_policies.append(policy)
    return resource_policy_list, related_policies


def gen_resource_instance_policy(vnf_list, resource_instance_policy):
    """Get policies governing resource instances in order to populate the Conductor API call"""
    cur_policies, _ = gen_policy_instance(vnf_list, resource_instance_policy, rtype='resourceInstanceProperty')
    return cur_policies


def gen_resource_region_policy(vnf_list, resource_region_policy):
    """Get policies governing resource region in order to populate the Conductor API call"""
    cur_policies, _ = gen_policy_instance(vnf_list, resource_region_policy, rtype='resourceRegionProperty')
    return cur_policies


def gen_inventory_group_policy(vnf_list, inventory_group_policy):
    """Get policies governing inventory group in order to populate the Conductor API call"""
    cur_policies, _ = gen_policy_instance(vnf_list, inventory_group_policy, rtype=None)
    return cur_policies


def gen_reservation_policy(vnf_list, reservation_policy):
    """Get policies governing resource instances in order to populate the Conductor API call"""
    cur_policies, _ = gen_policy_instance(vnf_list, reservation_policy, rtype='instanceReservationProperty')
    return cur_policies


def gen_distance_to_location_policy(vnf_list, distance_to_location_policy):
    """Get policies governing distance-to-location for VNFs in order to populate the Conductor API call"""
    cur_policies, related_policies = gen_policy_instance(vnf_list, distance_to_location_policy, rtype=None)
    for p_new, p_main in zip(cur_policies, related_policies):  # add additional fields to each policy
        properties = p_main['content']['distanceToLocationProperty']
        pcp_d = properties['distanceCondition']
        p_new[p_main['content']['identity']]['properties'] = {
            'distance': text_to_symbol[pcp_d['operator']] + " " + pcp_d['value'].lower(),
            'location': properties['locationInfo']
        }
    return cur_policies


def gen_attribute_policy(vnf_list, attribute_policy):
    """Get policies governing attributes of VNFs in order to populate the Conductor API call"""
    cur_policies, related_policies = gen_policy_instance(vnf_list, attribute_policy, rtype=None)
    for p_new, p_main in zip(cur_policies, related_policies):  # add additional fields to each policy
        properties = p_main['content']['cloudAttributeProperty']
        p_new[p_main['content']['identity']]['properties'] = {
            'evaluate': {
                'hypervisor': properties.get('hypervisor', ''),
                'cloud_version': properties.get('cloudVersion', ''),
                'cloud_type': properties.get('cloudType', ''),
                'dataplane': properties.get('dataPlane', ''),
                'network_roles': properties.get('networkRoles', ''),
                'complex': properties.get('complex', ''),
                'state': properties.get('state', ''),
                'country': properties.get('country', ''),
                'geo_region': properties.get('geoRegion', ''),
                'exclusivity_groups': properties.get('exclusivityGroups', ''),
                'replication_role': properties.get('replicationRole', '')
            }
        }
    return cur_policies


def gen_zone_policy(vnf_list, zone_policy):
    """Get zone policies in order to populate the Conductor API call"""
    cur_policies, related_policies = gen_policy_instance(vnf_list, zone_policy, rtype=None)
    for p_new, p_main in zip(cur_policies, related_policies):  # add additional fields to each policy
        pmz = p_main['content']['zoneProperty']
        p_new[p_main['content']['identity']]['properties'] = {'category': pmz['category'], 'qualifier': pmz['qualifier']}
    return cur_policies


def get_demand_properties(demand, policies):
    """Get list demand properties objects (named tuples) from policy"""
    def _get_candidates(candidate_info):
        return [dict(inventory_type=x['candidateType'], candidate_id=x['candidates']) for x in candidate_info]
    properties = []
    for policy in policies:
        for resourceInstanceType in policy['content']['resourceInstanceType']:
            if resourceInstanceType in demand['resourceModuleName']:
                for x in policy['content']['property']:
                    property = dict(inventory_provider=x['inventoryProvider'], 
                                    inventory_type=x['inventoryType'],
                                    service_resource_id=demand['serviceResourceId'])
                    if 'attributes' in x:
                        attributes = {}
                        for k,v in x['attributes'].items():
                            # key=data_mapping.convert(k)
                            key = k
                            attributes[key] = v
                            if(key=="model-invariant-id"):
                                attributes[key]=demand['resourceModelInfo']['modelInvariantId']
                            elif(key=="model-version-id"):
                                attributes[key]=demand['resourceModelInfo']['modelVersionId']
                        property.update({"attributes": attributes})
                    if x['inventoryType'] == "cloud":
                        property['region'] = {'get_param': "CHOSEN_REGION"}
                    if 'exclusionCandidateInfo' in demand:
                        property['excluded_candidates'] = _get_candidates(demand['exclusionCandidateInfo'])
                    if 'requiredCandidateInfo' in demand:
                        property['required_candidates'] = _get_candidates(demand['requiredCandidateInfo'])
                    properties.append(property)
    if len(properties) == 0:
        properties.append(dict(customer_id="", service_type="", inventory_provider="", inventory_type=""))
    return properties


def gen_demands(req_json, vnf_policies):
    """Generate list of demands based on request and VNF policies
    :param req_json: Request object from the client (e.g. MSO)
    :param vnf_policies: Policies associated with demand resources (e.g. from grouped_policies['vnfPolicy'])
    :return: list of demand parameters to populate the Conductor API call
    """
    demand_dictionary = {}
    for placementDemand in req_json['placementDemand']:
        demand_dictionary.update({placementDemand['resourceModuleName']: get_demand_properties(placementDemand, vnf_policies)})

    return demand_dictionary

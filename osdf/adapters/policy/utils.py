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

from collections import defaultdict
import itertools
from osdf.utils.programming_utils import dot_notation, list_flatten


def group_policies_gen(flat_policies, config):
    """Filter policies using the following steps:
    1. Apply prioritization among the policies that are sharing the same policy type and resource type
    2. Remove redundant policies that may applicable across different types of resource
    3. Filter policies based on type and return
    :param flat_policies: list of flat policies
    :return: Filtered policies
    """
    filtered_policies = defaultdict(list)
    policy_name = []
    policies = [x for x in flat_policies if x[list(x.keys())[0]]["type"]] # drop ones without 'type'
    priority = config.get('policy_info', {}).get('prioritization_attributes', {})
    aggregated_policies = dict()
    for plc in policies:
        attrs = [dot_notation(plc[list(plc.keys())[0]], dot_path) for key in priority.keys() for dot_path in priority[key]]
        attrs_list = [x if isinstance(x, list) else [x] for x in attrs]
        attributes = [list_flatten(x) if isinstance(x, list) else x for x in attrs_list]
        for y in itertools.product(*attributes):
            aggregated_policies.setdefault(y, [])
            aggregated_policies[y].append(plc)

    for key in aggregated_policies.keys():
        #aggregated_policies[key].sort(key=lambda x: x['priority'], reverse=True)
        prioritized_policy = aggregated_policies[key][0]
        if list(prioritized_policy.keys())[0] not in policy_name:
            # TODO: Check logic here... should policy appear only once across all groups?
            filtered_policies[prioritized_policy[list(prioritized_policy.keys())[0]]['type']].append(prioritized_policy)
            policy_name.append(list(prioritized_policy.keys())[0])

    return filtered_policies


def policy_name_as_regex(policy_name):
    """Get the correct policy name as a regex
    (e.g. OOF_HAS_vCPE.cloudAttributePolicy ends up in policy as OOF_HAS_vCPE.Config_MS_cloudAttributePolicy.1.xml
    So, for now, we query it as OOF_HAS_vCPE..*aicAttributePolicy.*)
    :param policy_name: Example: OOF_HAS_vCPE.aicAttributePolicy
    :return: regexp for policy: Example: OOF_HAS_vCPE..*aicAttributePolicy.*
    """
    p = policy_name.partition('.')
    return p[0] + p[1] + ".*" + p[2] + ".*"


def retrieve_node(req_json, reference):
    """
    Get the child node(s) from the dot-notation [reference] and parent [req_json].
    For placement and other requests, there are encoded JSONs inside the request or policy,
    so we need to expand it and then do a search over the parent plus expanded JSON.
    """
    req_json_copy = copy.deepcopy(req_json)
    info = dot_notation(req_json_copy, reference)
    return list_flatten(info) if isinstance(info, list) else info

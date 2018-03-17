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

from collections import defaultdict


def group_policies(flat_policies):
    """Filter policies using the following steps:
    1. Apply prioritization among the policies that are sharing the same policy type and resource type
    2. Remove redundant policies that may applicable across different types of resource
    3. Filter policies based on type and return
    :param flat_policies: list of flat policies
    :return: Filtered policies
    """
    aggregated_policies = {}
    filter_policies = defaultdict(list)
    policy_name = []
    for policy in flat_policies:
        policy_type = policy['content'].get('policyType')
        if not policy_type:
            continue
        if policy_type not in aggregated_policies:
            aggregated_policies[policy_type] = defaultdict(list)
        for resource in policy['content'].get('resourceInstanceType', []):
            aggregated_policies[policy_type][resource].append(policy)
    for policy_type in aggregated_policies:
        for resource in aggregated_policies[policy_type]:
            if len(aggregated_policies[policy_type][resource]) > 0:
                aggregated_policies[policy_type][resource].sort(key=lambda x: x['priority'], reverse=True)
                policy = aggregated_policies[policy_type][resource][0]
                if policy['policyName'] not in policy_name:
                    filter_policies[policy['content']['policyType']].append(policy)
                    policy_name.append(policy['policyName'])
    return filter_policies


def _regex_policy_name(policy_name):
    """Get the correct policy name as a regex
    (e.g. OOF_HAS_vCPE.cloudAttributePolicy ends up in policy as OOF_HAS_vCPE.Config_MS_cloudAttributePolicy.1.xml
    So, for now, we query it as OOF_HAS_vCPE..*aicAttributePolicy.*)
    :param policy_name: Example: OOF_HAS_vCPE.aicAttributePolicy
    :return: regexp for policy: Example: OOF_HAS_vCPE..*aicAttributePolicy.*
    """
    p = policy_name.partition('.')
    return p[0] + p[1] + ".*" + p[2] + ".*"

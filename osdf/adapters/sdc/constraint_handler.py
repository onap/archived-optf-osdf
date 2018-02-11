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

from osdf.config.base import osdf_config
from osdf.utils.programming_utils import dot_notation

ns = {'p': 'http://xmlns.onap.org/sdc/license-model/1.0'}
config_local = osdf_config.core


def choose_license(license_artifacts, order_info, service_type):
    entitlement_pool_uuids = []
    license_key_group_uuids = []

    for license_artifact in license_artifacts:
        for feature in license_artifact.findall('./p:feature-group-list/', ns):
            for entitlement in feature.findall('./p:entitlement-pool-list/', ns):
                if is_valid(entitlement, order_info, service_type):
                    entitlement_pool_uuid = entitlement.find('p:entitlement-pool-uuid', ns).text
                    entitlement_pool_uuids.append(entitlement_pool_uuid)
            for license_key_group in feature.findall('./p:license-key-group-list/', ns):
                if is_valid(license_key_group, order_info, service_type):
                    license_key_group_uuid = license_key_group.find('p:license-key-group-uuid', ns).text
                    license_key_group_uuids.append(license_key_group_uuid)
    return entitlement_pool_uuids, license_key_group_uuids


# element is expected to be a license-key-group or entitlement-pool
# if these elements diverge at a later date this method should be refactored
def is_valid(element, order_info, service_type):
    for limit in element.findall('./p:sp-limits/p:limit', ns):
        # description = limit.find('p:description', ns).text
        metric_value = limit.find('p:values', ns).text
        metric = limit.find('p:metric', ns).text
        try:
            order_value = dot_notation(order_info, config_local['service_info'][service_type][metric])
            # print("The order has the value %s for the metric %s and the limit specifies the value %s. The limit has the description %s." % (order_value, metric, metric_value, description))
            if isinstance(order_value, list): # it is possible a list is returned, for example a list of vnfs for vCPE
                for arr_value in order_value:
                    if str(metric_value) != str(arr_value):
                        return False
            else:
                if str(metric_value) != str(order_value):
                    return False
        except KeyError:
            return False
    # vendor limits
    for limit in element.findall('./p:vendor-limits/p:limit', ns):
            # description = limit.find('p:description', ns).text
            metric_value = limit.find('p:values', ns).text
            metric = limit.find('p:metric', ns).text
            try:
                order_value = dot_notation(order_info, config_local['service_info'][service_type][metric])
                if isinstance(order_value, list): # it is possible a list is returned, for example a list of vnfs for vCPE
                    for arr_value in order_value:
                        if str(metric_value) != str(arr_value):
                            return False
                else:
                    if str(metric_value) != str(order_value):
                        return False
                # print("The order has the value %s for the metric %s and the limit specifies the value %s. The limit has the description %s." % (order_value, metric, metric_value, description))

            except KeyError:
                return False
    return True


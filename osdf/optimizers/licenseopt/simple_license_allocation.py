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

from requests import RequestException
from osdf.datasources.sdc import sdc, constraint_handler
from osdf.logging.osdf_logging import audit_log, metrics_log, MH
from osdf.config.base import osdf_config
from osdf.utils import data_mapping


def license_optim(request_json):
    """
    Fetch license artifacts associated with the service model and search licensekey-group-UUID and entitlement-pool-uuid
    associated with the given att part number and nominal throughput in a request
    :param request_json: Request in a JSON format
    :return: A tuple of licensekey-group-uuid-list and entitlement-group-uuid-list
    """
    req_id = request_json["requestInfo"]["requestId"]
    config = osdf_config.deployment

    model_name = request_json['placementInfo']['serviceModelInfo']['modelName']
    service_name = data_mapping.get_service_type(model_name)

    license_info = []

    order_info = json.loads(request_json["placementInfo"]["orderInfo"])
    if service_name == 'VPE':
        data_mapping.normalize_user_params(order_info)
    for licenseDemand in request_json['placementInfo']['demandInfo']['licenseDemand']:
        metrics_log.info(MH.requesting("sdc", req_id))
        license_artifacts = sdc.request(licenseDemand['resourceModelInfo']['modelVersionId'],request_json["requestInfo"]["requestId"], config)
        entitlement_pool_uuids, license_key_group_uuids = constraint_handler.choose_license(license_artifacts,order_info, service_name)
        license_info.append(
            {'serviceResourceId': licenseDemand['serviceResourceId'],
             'resourceModuleName': licenseDemand['resourceModuleName'],
             'entitlementPoolList': entitlement_pool_uuids,
             'licenseKeyGroupList': license_key_group_uuids
             })
    return license_info

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


def license_optim(request_json):
    """
    Fetch license artifacts associated with the service model and search licensekey-group-UUID and entitlement-pool-uuid
    associated with the given att part number and nominal throughput in a request
    :param request_json: Request in a JSON format
    :return: A tuple of licensekey-group-uuid-list and entitlement-group-uuid-list
    """
    req_id = request_json["requestInfo"]["requestId"]

    model_name = request_json.get('placementInfo', {}).get('serviceInfo', {}).get('modelInfo', {}).get('modelName')
    service_name = model_name

    license_info = []

    for licenseDemand in request_json.get('placementInfo', {}).get('demandInfo', {}).get('licenseDemands', []):
        license_info.append(
            {'serviceResourceId': licenseDemand['serviceResourceId'],
             'resourceModuleName': licenseDemand['resourceModuleName'],
             'entitlementPoolList': "NOT SUPPORTED",
             'licenseKeyGroupList': "NOT SUPPORTED"
             })
    return license_info

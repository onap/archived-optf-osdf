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

from osdf.utils.interfaces import RestClient
import xml.etree.ElementTree as ET

def request(model_version_id, request_id, config):
    """Get all of the license artifacts from SDC using service_resource_id and model_version_id
    :param model_version_id: model_version_id
    :param request_id: request_id
    :return: license artifacts from SDC
    """
    base_url = config['sdcUrl']
    uid, passwd = config['sdcUsername'], config['sdcPassword']
    headers = {"CSP_UID": config['sdcMechId'], "X-ONAP-InstanceID": "osdf"}
    rc = RestClient(userid=uid, passwd=passwd, headers=headers, method="GET", req_id=request_id)
    resource_data = rc.request(base_url + '/resources/{}/metadata'.format(model_version_id))

    artifact_ids = [x['artifactURL'].split("/resources/")[-1]  # get the part after /resources/
                    for x in resource_data.get('artifacts', []) if x.get('artifactType') == "VF_LICENSE"]
    artifact_urls = [base_url + '/resources/' + str(artifact_id) for artifact_id in artifact_ids]
    licenses = []
    for x in artifact_urls:
        licenses.append(ET.fromstring(rc.request(x, asjson=False)))
    return licenses

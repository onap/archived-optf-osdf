# -------------------------------------------------------------------------
#   Copyright (c) 2018 Huawei Intellectual Property
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

import requests
from requests.auth import HTTPBasicAuth


class RouteOpt:

    """
    This values will need to deleted.. 
    only added for the debug purpose 
    """
    aai_host = "https:\\192.168.17.26:8443"
    aai_headers = {
        "X-TransactionId": "9999",
        "X-FromAppId": "OOF",
        "Content-Type": "application/json",
        "Real-Time": "true"
    }


    def getRoute(self, request):
        """
        This method checks 
        :param logical_link:
        :return:
        """

        print(request["srcPort"])
        print(request["dstport"])
        src_access_node_id = request["srcPort"]["src-access-node-id"]
        dst_access_node_id = request["dstPort"]["dst-access-node-id"]

        ingress_p_interface = None
        egress_p_interface = None

        logical_links = self.get_logical_links()

            """
            TODO: Logic to be extended for the repose filling
            """

            
        def get_logical_links(self):
        """
                    This method returns list of all cross ONAP links
                    from /aai/v14/network/logical-links?operation-status="Up"
                    :return: logical-links[]
        """
        logical_link_url = "/aai/v14/network/logical-links?operation-status=\"Up\""
        aai_req_url = self.aai_host + logical_link_url

        response = requests.get(aai_req_url,
                     headers=self.aai_headers,
                     auth=HTTPBasicAuth("", ""))

        if response.status_code == 200:
            return response.json

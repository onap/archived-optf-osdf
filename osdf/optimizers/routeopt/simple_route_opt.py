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

    def isCrossONAPLink(self, logical_link):
        """
        This method checks if cross link is cross onap
        :param logical_link:
        :return:
        """
        for relationship in logical_link["logical-links"]["relationsihp-list"]["relationship"]:
            if relationship["related-to"] == "p-interface":
                if "external" in relationship["related-link"]:
                    return True
        return False

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
        
        # for the case of request for same domain, return the same node with destination update
        if(src_access_node_id == dst_access_node_id)
            return {
                [
                    {
                        "access-topology-id": request["srcPort"]["src-access-topology-id"],
                        "access-client-id": request["srcPort"]["access-client-id"],
                        "access-provider-id": request["srcPort"]["access-provider-id"],
                        "access-node-id": request["srcPort"]["access-node-id"],
                        "src-access-ltp-id": request["srcPort"]["src-access-ltp-id"],
                        "dst-access-ltp-id": request["dstPort"]["dst-access-ltp-id"]
                    }
                ]
            } 

        ingress_p_interface = None
        egress_p_interface = None

        logical_links = self.get_logical_links()

        # take the logical link where both the p-interface in same onap
        if logical_links != None:
            for logical_link in logical_links["results"]:
                if not self.isCrossONAPLink(logical_link):

                    # link is in local ONAP
                    for relationship in logical_link["logical-links"]["relationsihp-list"]["relationship"]:
                        if relationship["related-to"] == "p-interface":
                            if src_access_node_id in relationship["related-link"]:
                                ingress_p_interface = relationship["related-link"].split("/")[-1]
                            if dst_access_node_id in relationship["related-link"]:
                                egress_p_interface = relationship["related-link"].split("/")[-1]

            return {
                [
                    {
                        "access-topology-id": request["srcPort"]["src-access-topology-id"],
                        "access-client-id": request["srcPort"]["access-client-id"],
                        "access-provider-id": request["srcPort"]["access-provider-id"],
                        "access-node-id": request["srcPort"]["access-node-id"],
                        "src-access-ltp-id": request["srcPort"]["src-access-ltp-id"],
                        "dst-access-ltp-id": ingress_p_interface
                    },
                    {
                        "access-topology-id": request["dstPort"]["access-topology-id"],
                        "access-client-id": request["dstPort"]["access-client-id"],
                        "access-provider-id": request["dstPort"]["access-provider-id"],
                        "access-node-id": request["dstPort"]["access-node-id"],
                        "src-access-ltp-id": egress_p_interface,
                        "dst-access-ltp-id": request["dstPort"]["dst-access-ltp-id"]
                    }
                ]
            }



    def get_pinterface(self, url):
        """
        This method returns details for p interface
        :return: details of p interface
        """
        aai_req_url = self.aai_host + url
        response = requests.get(aai_req_url,
                                headers=self.aai_headers,
                                auth=HTTPBasicAuth("", ""))

        if response.status_code == 200:
            return response.json


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

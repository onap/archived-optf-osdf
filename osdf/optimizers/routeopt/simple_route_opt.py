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
    # DNS server and standard port of AAI.. 
    # TODO: read the port from the configuration and add to DNS
    aai_host = "https://aai.api.simpledemo.onap.org:8443"
    aai_headers = {
        "X-TransactionId": "9999",
        "X-FromAppId": "OOF",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Real-Time": "true"
    }

    def isCrossONAPLink(self, logical_link):
        """
        This method checks if cross link is cross onap
        :param logical_link:
        :return:
        """
        for relationship in logical_link["relationship-list"]["relationship"]:
            if relationship["related-to"] == "ext-aai-network":
                return True
        return False

    def getRoute(self, request):
        """
        This method checks 
        :param logical_link:
        :return:
        """

        src_access_node_id = request["srcPort"]["src-access-node-id"]
        dst_access_node_id = request["dstPort"]["dst-access-node-id"]
        

        ingress_p_interface = None
        egress_p_interface = None

        # for the case of request_json for same domain, return the same node with destination update
        if src_access_node_id == dst_access_node_id:
            data = '{'\
                '"vpns":['\
                    '{'\
                        '"access-topology-id": "' + request["srcPort"]["src-access-topology-id"] + '",'\
                        '"access-client-id": "' + request["srcPort"]["src-access-client-id"] + '",'\
                        '"access-provider-id": "' + request["srcPort"]["src-access-provider-id"]+ '",'\
                        '"access-node-id": "' + request["srcPort"]["src-access-node-id"]+ '",'\
                        '"src-access-ltp-id": "' + request["srcPort"]["src-access-ltp-id"]+ '",'\
                        '"dst-access-ltp-id": "' + request["dstPort"]["dst-access-ltp-id"]  +'"'\
                    '}'\
                ']'\
            '}'
            return data
        else:
            logical_links = self.get_logical_links()

            # take the logical link where both the p-interface in same onap
            if logical_links != None:
                for logical_link in logical_links.get("logical-link"):
                    if not self.isCrossONAPLink(logical_link):
                        # link is in local ONAP
                        for relationship in logical_link["relationship-list"]["relationship"]:
                            if relationship["related-to"] == "p-interface":
                                if src_access_node_id in relationship["related-link"]:
                                    i_interface = relationship["related-link"].split("/")[-1]
                                    ingress_p_interface = i_interface.split("-")[-1]
                                if dst_access_node_id in relationship["related-link"]:
                                    e_interface = relationship["related-link"].split("/")[-1]
                                    egress_p_interface = e_interface.split("-")[-1]
                        data = '{'\
                                '"vpns":['\
                                        '{'\
                                        '"access-topology-id": "' + request["srcPort"]["src-access-topology-id"] + '",'\
                                        '"access-client-id": "' + request["srcPort"]["src-access-client-id"] + '",'\
                                        '"access-provider-id": "' + request["srcPort"]["src-access-provider-id"]+ '",'\
                                        '"access-node-id": "' + request["srcPort"]["src-access-node-id"]+ '",'\
                                        '"src-access-ltp-id": "' + request["srcPort"]["src-access-ltp-id"]+ '",'\
                                        '"dst-access-ltp-id": "' + ingress_p_interface +'"'\
                                '},'\
                                '{' \
                                        '"access-topology-id": "' + request["dstPort"]["dst-access-topology-id"] + '",' \
                                        '"access-topology-id": "' + request["dstPort"]["dst-access-topology-id"]+ '",' \
                                        '"access-provider-id": "' + request["dstPort"]["dst-access-provider-id"]+ '",' \
                                        '"access-node-id": "' + request["dstPort"]["dst-access-node-id"]+ '",' \
                                        '"src-access-ltp-id": "' + egress_p_interface + '",' \
                                        '"dst-access-ltp-id": "' + request["dstPort"]["dst-access-ltp-id"] + '"' \
                                '}'\
                            ']'\
                        '}'
                        return data


    def get_pinterface(self, url):
        """
        This method returns details for p interface
        :return: details of p interface
        """
        aai_req_url = self.aai_host + url
        response = requests.get(aai_req_url,
                                headers=self.aai_headers,
                                auth=HTTPBasicAuth("AAI", "AAI"),
                                verify=False)

        if response.status_code == 200:
            return response.json()


    def get_logical_links(self):
        """
        This method returns list of all cross ONAP links
        from /aai/v14/network/logical-links?operation-status="Up"
        :return: logical-links[]
        """
        logical_link_url = "/aai/v13/network/logical-links?operational-status=up"
        aai_req_url = self.aai_host + logical_link_url

        response = requests.get(aai_req_url,
                     headers=self.aai_headers,
                     auth=HTTPBasicAuth("AAI", "AAI"),
                     verify=False)

        logical_links =  None
        if response.status_code == 200:
            return response.json()
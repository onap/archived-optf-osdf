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

from osdf.utils.mdc_utils import mdc_from_json
from osdf.logging.osdf_logging import MH, audit_log, error_log, debug_log

import pymzn


class RouteOpt:
    """
    This values will need to deleted.. 
    only added for the debug purpose 
    """
    # DNS server and standard port of AAI.. 
    # TODO: read the port from the configuration and add to DNS
    # aai_host = "https://aai.api.simpledemo.onap.org:8443"
    aai_host = "http://127.0.0.1:8443"
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

    def solve(self, mzn_model, dzn_data):
        return pymzn.minizinc(mzn=mzn_model, data=dzn_data)

    def convert(self,routes):
        # TODO: minizinc response will be of [[1, 2, 3], [1, 4, 3]] format. Needs to be converted to [["cross-link-1", "cross-link-2"], ["cross-link-3", "cross-link-4"]]
        return 

    def getLinks(self, mzn_model, dzn_data):
        audit_log.info("get links==>")
        routes = self.solve(mzn_model, dzn_data)
        audit_log.info("mocked minizinc solution====>")
        audit_log.info(routes)
        links=convert(routes)
        return links



    def build_dzn_data(self, src_access_node_id, dst_access_node_id):
        dzn_data = {}
        # TODO: data to be prepared in the below format:
        # dzn_data = {
        #             'N': 5,
        #             'M': 6,
        #             'Edge_Start': [1,1,1,2,3,4],
        #             'Edge_End': [2,3,4,5,4,5],
        #             'L': [1,1,1,1,1,1],
        #             'Start': 1,
        #             'End': 5,
        #         }

        audit_log.info("src_access_node_id")
        audit_log.info(src_access_node_id)

        audit_log.info("dst_access_node_id")
        audit_log.info(dst_access_node_id)

        logical_links = self.get_logical_links()
        audit_log.info("mocked response of AAI received (logical links) successful===>")
        audit_log.info(logical_links)

        # take the logical link where both the p-interface in same onap
        if logical_links != None:
            # for logical_link in logical_links:
            #     status = self.isCrossONAPLink(logical_link)
            #     if not self.isCrossONAPLink(logical_link):
            #         # link is in local ONAP
            #         for relationship in logical_link["relationship-list"]["relationship"]:
            #             if relationship["related-to"] == "p-interface":
            #                 if src_access_node_id in relationship["accessNodeId"]:
            #                     i_interface = relationship["related-link"].split("/")[-1]
            #                     ingress_p_interface = i_interface.split("-")[-1]
            #
            #                 if dst_access_node_id in relationship["accessNodeId"]:
            #                     e_interface = relationship["related-link"].split("/")[-1]
            #                     egress_p_interface = e_interface.split("-")[-1]
            return dzn_data

    def getRoute(self, request):
        """
        This method checks 
        :param logical_link:
        :return:
        """
        request_status = "accepted"
        routeInfo = request["routeInfo"]["routeRequests"]
        routeRequest = routeInfo[0]
        src_access_node_id = routeRequest["srcPort"]["accessNodeId"]
        dst_access_node_id = routeRequest["dstPort"]["accessNodeId"]

        dzn_data = self.build_dzn_data(src_access_node_id, dst_access_node_id) 
        audit_log.info("recevied dzn data====>")
        audit_log.info(dzn_data)
        mzn_model = os.path.join(BASE_DIR, 'route_opt.mzn')
        routeSolutions = self.getLinks(mzn_model, dzn_data)
        data = {
            "requestId": request["requestInfo"]["requestId"],
            "transactionId": request["requestInfo"]["transactionId"],
            "statusMessage": " ",
            "requestStatus": request_status,
            "solutions": routeSolutions
        }
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

        logical_links = None
        if response.status_code == 200:
            return response.json()

# -------------------------------------------------------------------------
#   Copyright (c) 2020 Fujitsu Limited Intellectual Property
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
import unittest

from unittest.mock import patch
from apps.route.optimizers.inter_domain_route_opt import InterDomainRouteOpt
import osdf.config.loader as config_loader
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict

count = 1 

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
  
    main_dir = ""
    response_data_file = main_dir + "test/inter_domain_route_opt/get_links.json"
    bandwidth_attributes = main_dir + "test/inter_domain_route_opt/bandwidth_attributes.json"
    bandwidth_attribute_values = json_from_file(bandwidth_attributes)
    
    controllers_list = main_dir + "test/inter_domain_route_opt/controllers_list.json"
    
    if args[0] == 'https://api.url:30233/aai/v19/network/logical-links?link-type=inter-domain&operational-status=up':
        return MockResponse(json_from_file(response_data_file), 200)
    elif args[0] == 'https://api.url:30233/aai/v19/network/pnfs/pnf/pnf1/p-interfaces/p-interface/int1?depth=all':
        return MockResponse(bandwidth_attribute_values["int-1-bw"], 200)
    elif args[0] == 'https://api.url:30233/aai/v19/network/pnfs/pnf/pnf2/p-interfaces/p-interface/int3?depth=all':
        return MockResponse(bandwidth_attribute_values["int-3-bw"], 200)
    elif args[0] == 'https://api.url:30233/aai/v19/network/pnfs/pnf/pnf2/p-interfaces/p-interface/int4?depth=all':
        return MockResponse(bandwidth_attribute_values["int-4-bw"], 200)
    elif args[0] == 'https://api.url:30233/aai/v19/network/pnfs/pnf/pnf3/p-interfaces/p-interface/int5?depth=all':
        return MockResponse(bandwidth_attribute_values["int-5-bw"], 200)
    elif args[0] == 'https://api.url:30233/aai/v19/network/pnfs/pnf/pnf3/p-interfaces/p-interface/int6?depth=all':
        return MockResponse(bandwidth_attribute_values["int-6-bw"], 200)
    elif args[0] == 'https://api.url:30233/aai/v19/network/pnfs/pnf/pnf4/p-interfaces/p-interface/int7?depth=all':
        return MockResponse(bandwidth_attribute_values["int-7-bw"], 200)
    elif args[0] == 'https://api.url:30233/aai/v19/external-system/esr-thirdparty-sdnc-list':
        return MockResponse(json_from_file(controllers_list), 200)                                             
    return MockResponse(None, 404)   
    

def mocked_requests_put(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data
    main_dir = ""
    controllers_for_interfaces = main_dir + "test/inter_domain_route_opt/controllers_for_interfaces.json"
    controllers_for_interfaces_values = json_from_file(controllers_for_interfaces)

    global count
      
    if count == 1:
        count += 1
        return MockResponse(controllers_for_interfaces_values["int-1-cont"], 200)
    elif count == 2:
        count += 1
        return MockResponse(controllers_for_interfaces_values["int-3-cont"], 200)
    elif count == 3:
        count += 1
        return MockResponse(controllers_for_interfaces_values["int-4-cont"], 200)
    elif count == 4:
        count += 1
        return MockResponse(controllers_for_interfaces_values["int-5-cont"], 200)
    elif count == 5:
      count += 1
      return MockResponse(controllers_for_interfaces_values["int-6-cont"], 200)
    elif count == 6:
        count += 1
        return MockResponse(controllers_for_interfaces_values["int-7-cont"], 200)
            
    return MockResponse(None, 404)            
    
            

class TestInterDomainRouteOpt(unittest.TestCase):
    @patch('apps.route.optimizers.inter_domain_route_opt.requests.get', side_effect=mocked_requests_get)
    @patch('apps.route.optimizers.inter_domain_route_opt.requests.put', side_effect=mocked_requests_put)
    @patch('apps.route.optimizers.simple_route_opt.pymzn.minizinc')               
    def test_process_get_route(self, mock_solve , mock_put, mock_get):      
        main_dir = ""
        mock_solve.return_value = [{'x': [1, 1, 0, 0, 0, 0]}]
        self.config_spec = {
            "deployment": "test/functest/simulators/simulated-config/osdf_config.yaml",
            "core": "test/functest/simulators/simulated-config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))
        parameter_data_file = main_dir + "test/inter_domain_route_opt/request.json"
        request_json = json_from_file(parameter_data_file)
        routopt = InterDomainRouteOpt()
        actual_response = routopt.get_route(request_json,self.osdf_config)
        mock_response = {
            "requestId":"789456",
            "transactionId":"123456",
            "statusMessage":"SUCCESS",
            "requestStatus":"accepted",
            "solutions":{
                "routeInfo":{
                "serviceRoute":[
                    {
                     "srcInterfaceId":"int19",
                     "dstInterfaceId":"int1",
                     "controllerId":"Controller1"
                },
                    {
                     "srcInterfaceId":"int3",
                     "dstInterfaceId":"int4",
                     "controllerId":"Controller2"
                },
                    {
                     "srcInterfaceId":"int5",
                     "dstInterfaceId":"int20",
                     "controllerId":"Controller3"
                }
                ],
               "linkList":[
                    "link1",
                    "link2"
                ]
                }
           }
        }
        self.assertEqual(mock_response, actual_response)
        
        
if __name__ == '__main__':
    unittest.main()
        
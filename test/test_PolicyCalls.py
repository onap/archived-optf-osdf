import json
import unittest

from osdf.config.base import osdf_config
from osdf.adapters.policy import interface
from osdf.utils.interfaces import RestClient
import yaml
from mock import patch
from osdf.optimizers.placementopt.conductor import translation


class TestPolicyCalls(unittest.TestCase):
        
    def test_get_subscriber_name(self):
        req_json_obj = json.loads(open("./test/placement-tests/request_mso.json").read())
        config_core = osdf_config.core
        pmain = config_core['policy_info']['placement']
        print(pmain)
        subs_name = interface.get_subscriber_name(req_json_obj, pmain)
        print("subscriber_name=", subs_name)
        self.assertEquals(subs_name, "Avteet_Chayal")
    
    
    def test_get_subscriber_name_null(self):
        req_json_file = "./test/placement-tests/request_mso_subs_name_null.json"
        req_json_obj = json.loads(open(req_json_file).read())
        config_core = osdf_config.core
        
        pmain = config_core['policy_info']['placement']
        print(pmain)
        subs_name = interface.get_subscriber_name(req_json_obj, pmain)
        print("subscriber_name=", subs_name)
        self.assertEquals(subs_name, "DEFAULT")
        
    
    def test_get_subscriber_name_blank(self):
        req_json_file = "./test/placement-tests/request_mso_subs_name_blank.json"
        req_json_obj = json.loads(open(req_json_file).read())
        config_core = osdf_config.core
        
        pmain = config_core['policy_info']['placement']
        print(pmain)
        subs_name = interface.get_subscriber_name(req_json_obj, pmain)
        print("subscriber_name=", subs_name)
        self.assertEquals(subs_name, "DEFAULT")
        
    
    def test_get_subscriber_name_default(self):
        req_json_file = "./test/placement-tests/request_mso_subs_name_default.json"
        req_json_obj = json.loads(open(req_json_file).read())
        config_core = osdf_config.core
        
        pmain = config_core['policy_info']['placement']
        print(pmain)
        subs_name = interface.get_subscriber_name(req_json_obj, pmain)
        print("subscriber_name=", subs_name)
        self.assertEquals(subs_name, "DEFAULT")
    
    
    def test_get_subscriber_name_none(self):
        req_json_file = "./test/placement-tests/request_mso_subs_name_none.json"
        req_json_obj = json.loads(open(req_json_file).read())
        config_core = osdf_config.core
        
        pmain = config_core['policy_info']['placement']
        print(pmain)
        subs_name = interface.get_subscriber_name(req_json_obj, pmain)
        print("subscriber_name=", subs_name)
        self.assertEquals(subs_name, "DEFAULT")
        
    
    def test_get_by_scope(self):
        req_json_file = "./test/placement-tests/testScoperequest.json"
        allPolicies = "./test/placement-tests/scopePolicies.json"
        req_json_obj = json.loads(open(req_json_file).read())
        req_json_obj2 = json.loads(open(allPolicies).read())
        config_core = osdf_config.core
        yamlFile = "./test/placement-tests/test_by_scope.yaml"
        
        with open(yamlFile) as yamlFile2:
            policyConfigFile = yaml.load(yamlFile2)
            with patch('osdf.adapters.policy.interface.get_subscriber_role', return_value=('FFA Homing', [])) as mock_open:
                with patch('osdf.utils.interfaces.RestClient.request', return_value = req_json_obj2):
                    policiesList = interface.get_by_scope(RestClient, req_json_obj, policyConfigFile, 'placement')
                    print(policiesList)
                    #catches Exception if policiesList is null
                    self.assertTrue(policiesList, 'is null')
                    self.assertRaises(Exception)
    
    def test_gen_demands(self):
        actionsList = []
        genDemandslist = []
        req_json = "./test/placement-tests/testScoperequest.json"
        policiesList = "./test/placement-tests/vnfGroupPolicies.txt"
        fh = json.loads(open(policiesList).read())
        #print(fh)
        req_json = json.loads(open(req_json).read())
        config_core = osdf_config.core
        service_type = req_json['placementInfo'].get('serviceType', None)
        # service_type = data_mapping.get_request_service_type(req_json_file)
        genDemands = translation.gen_demands(req_json['placementInfo']['demandInfo'], fh)
        #print(genDemands)
        #print(req_json_file['placementInfo']['demandInfo']['placementDemand'][0])
        for action in req_json['placementInfo']['demandInfo']['placementDemand']:
            #print(action['resourceModuleName'])
            actionsList.append(action['resourceModuleName'])
        for key2,value in genDemands.items():
            #print(key2)
            genDemandslist.append(key2)
        #genDemandslist.remove('Primary IP_Mux_Demux updated_1 0')
        #catches Exception if lists are not equal
        self.assertListEqual(genDemandslist, actionsList, 'generated demands are not equal to the passed input [placementDemand][resourceModuleName] list')
           
if __name__ == '__main__':
    unittest.main()

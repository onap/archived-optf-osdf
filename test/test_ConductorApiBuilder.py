import unittest
import json
import yaml
from osdf.optimizers.placementopt.conductor.api_builder import conductor_api_builder


class TestConductorApiBuilder(unittest.TestCase):

    def test_conductor_api_call_builder(self):
        #main_dir = ".."
        main_dir = ""
        conductor_api_template = main_dir + "osdf/templates/conductor_interface.json"
        parameter_data_file = main_dir + "test/placement-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"
        local_config_file = main_dir + "config/common_config.yaml"

        policy_data_files = ["CloudAttributePolicy_vGMuxInfra_1.json",
                            "CloudAttributePolicy_vG_1.json",
                            "DistanceToLocationPolicy_vGMuxInfra_1.json",
                            "DistanceToLocationPolicy_vG_1.json",
                            "InventoryGroup_vGMuxInfra_1.json",
                            "InventoryGroup_vG_1.json",
                            "PlacementOptimizationPolicy.json",
                            "ResourceInstancePolicy_vG_1.json",
                            "VNFPolicy_vGMuxInfra_1.json",
                            "VNFPolicy_vG_1.json",
                            "ZonePolicy_vGMuxInfra_1.json",
                            "ZonePolicy_vG_1.json"]
        request_json = json.loads(open(parameter_data_file).read())
        policies = [json.loads(open(policy_data_path + file).read()) for file in policy_data_files]
        local_config = yaml.load(open(local_config_file))
        templ_string = conductor_api_builder(request_json, policies, local_config, [], conductor_api_template)
        templ_json = json.loads(templ_string)
        self.assertEqual(templ_json["name"], "yyy-yyy-yyyy")


if __name__ == "__main__":
    unittest.main()


# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
#   Copyright (C) 2020 Wipro Limited.
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
import unittest

from osdf.adapters.conductor import conductor
import osdf.config.loader as config_loader
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict
from osdf.adapters.policy import interface as pol


class TestConductorCalls(unittest.TestCase):

    def setUp(self):
        self.config_spec = {
            "deployment": "test/functest/simulators/simulated-config/osdf_config.yaml",
            "core": "test/functest/simulators/simulated-config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))
        self.lp = self.osdf_config.core.get('osdf_temp', {}).get('local_policies', {}
                                                                 ).get('placement_policy_files_vcpe')
        self.template_fields = {
            'location_enabled': True,
            'version': '2017-10-10'
        }

    def tearDown(self):
        pass

    def test_request(self):
        req_json = json_from_file("./test/placement-tests/request.json")
        policies = pol.get_local_policies("test/policy-local-files/", self.lp)
        req_info = req_json['requestInfo']
        demands = req_json['placementInfo']['placementDemands']
        request_parameters = req_json['placementInfo']['requestParameters']
        service_info = req_json['serviceInfo']
        conductor.request(req_info, demands, request_parameters, service_info, self.template_fields,
                          self.osdf_config, policies)

    def test_request_vfmod(self):
        req_json = json_from_file("./test/placement-tests/request_vfmod.json")
        policies = pol.get_local_policies("test/policy-local-files/", self.lp)
        req_info = req_json['requestInfo']
        demands = req_json['placementInfo']['placementDemands']
        request_parameters = req_json['placementInfo']['requestParameters']
        service_info = req_json['serviceInfo']
        conductor.request(req_info, demands, request_parameters, service_info, self.template_fields,
                          self.osdf_config, policies)


if __name__ == "__main__":
    unittest.main()


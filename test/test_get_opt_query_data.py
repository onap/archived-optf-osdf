# -------------------------------------------------------------------------
#   Copyright (c) 2017-2018 AT&T Intellectual Property
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
import json
from osdf.adapters.conductor.translation import get_opt_query_data


class TestGetOptQueryData(unittest.TestCase):

    def test_get_opt_query_data(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/placement-tests/request.json"
        policy_data_path = main_dir + "test/policy-local-files/"

        query_policy_data_file = ["QueryPolicy_vCPE.json"]
        request_json = json.loads(open(parameter_data_file).read())
        policies = [json.loads(open(policy_data_path + file).read()) for file in query_policy_data_file]
        req_param_dict = get_opt_query_data(request_json['placementInfo']['requestParameters'], policies)

        self.assertTrue(req_param_dict is not None)

    def test_get_opt_query_data_vfmod(self):
        main_dir = ""
        parameter_data_file = main_dir + "test/placement-tests/request_vfmod.json"
        policy_data_path = main_dir + "test/policy-local-files/"

        query_policy_data_file = ["QueryPolicy_vFW_TD.json"]
        request_json = json.loads(open(parameter_data_file).read())
        policies = [json.loads(open(policy_data_path + file).read()) for file in query_policy_data_file]
        req_param_dict = get_opt_query_data(request_json['placementInfo']['requestParameters'], policies)

        self.assertTrue(req_param_dict is not None)


if __name__ == "__main__":
    unittest.main()


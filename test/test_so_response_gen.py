# -------------------------------------------------------------------------
#   Copyright (c) 2017-2018 AT&T Intellectual Property
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
import yaml
from osdf.utils.interfaces import json_from_file
from osdf.optimizers.placementopt.conductor.conductor import conductor_response_processor
from osdf.utils.interfaces import RestClient


class TestSoResponseGen(unittest.TestCase):
    def setUp(self):
        main_dir = ""
        conductor_response_file = main_dir + "test/placement-tests/conductor_response.json"
        self.conductor_res = json_from_file(conductor_response_file)
        self.rc = RestClient()

    def test_so_response_gen(self):
        res = conductor_response_processor(self.conductor_res, self.rc, "test")
        self.assertEqual(len(res['solutions']['placementSolutions'][0]), 2)


if __name__ == "__main__":
    unittest.main()
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

from osdf.adapters.local_data import local_policies


class TestLocalPolicies(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.folder = './test/policy-local-files'
        self.invalid_policies = ['INVALID-one.json', 'INVALID-two.json']
        self.valid_policies = ['CloudAttributePolicy_vG_1.json', 'CloudAttributePolicy_vGMuxInfra_1.json']
       
    def test_get_local_policies_no_policies(self):
        with self.assertRaises(FileNotFoundError):
             res = local_policies.get_local_policies(self.folder, self.invalid_policies)
             assert res is None

    def test_get_local_valid_policies(self):
        res = local_policies.get_local_policies(self.folder, self.valid_policies)
        assert len(res) == len(self.valid_policies)

    def test_get_subset_valid_policies(self):
        wanted = [ x[:-5] for x in self.valid_policies[:1] ]
        res = local_policies.get_local_policies(self.folder, self.valid_policies, wanted)
        assert len(res) == len(wanted)


if __name__ == "__main__":
    unittest.main()


# -------------------------------------------------------------------------
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

import copy
from mock import patch
import unittest
from apps.pci.optimizers.solver.ml_model import MlModel
from osdf.adapters.dcae.des import DESException
import osdf.config.loader as config_loader
from osdf.utils.interfaces import json_from_file
from osdf.utils.programming_utils import DotDict


class TestMlModel(unittest.TestCase):
    def setUp(self):
        self.config_spec = {
            "deployment": "config/osdf_config.yaml",
            "core": "config/common_config.yaml"
        }
        self.osdf_config = DotDict(config_loader.all_configs(**self.config_spec))

    def tearDown(self):
        pass

    def test_ml_model(self):
        des_result_file = 'test/apps/pci_optimization/des_result.json'
        results = json_from_file(des_result_file)

        dzn_data = {
            'NUM_NODES': 4,
            'NUM_PCIS': 4,
            'NUM_NEIGHBORS': 4,
            'NEIGHBORS': [],
            'NUM_SECOND_LEVEL_NEIGHBORS': 1,
            'SECOND_LEVEL_NEIGHBORS': [],
            'PCI_UNCHANGEABLE_CELLS': [],
            'ORIGINAL_PCIS': []
        }

        network_cell_info = {
            'cell_list': [
                {
                    'cell_id': 'Chn0001',
                    'id': 1,
                    'nbr_list': []
                },
                {
                    'cell_id': 'Chn0002',
                    'id': 2,
                    'nbr_list': []
                }
            ]
        }
        self.patcher_req = patch('osdf.adapters.dcae.des.extract_data', side_effect=results)
        self.Mock_req = self.patcher_req.start()
        mlmodel = MlModel(self.osdf_config)
        mlmodel.get_additional_inputs(dzn_data, network_cell_info)
        self.assertEqual(['Chn0001'], dzn_data['PCI_UNCHANGEABLE_CELLS'])
        self.patcher_req.stop()

        dzn_data['PCI_UNCHANGEABLE_CELLS'] = []
        self.patcher_req = patch('osdf.adapters.dcae.des.extract_data', side_effect=DESException('error'))
        self.Mock_req = self.patcher_req.start()
        mlmodel.get_additional_inputs(dzn_data, network_cell_info)
        self.assertEqual([], dzn_data['PCI_UNCHANGEABLE_CELLS'])
        self.patcher_req.stop()

        self.patcher_req = patch('osdf.adapters.dcae.des.extract_data', return_value=[])
        self.Mock_req = self.patcher_req.start()
        mlmodel.get_additional_inputs(dzn_data, network_cell_info)
        self.assertEqual([], dzn_data['PCI_UNCHANGEABLE_CELLS'])
        self.patcher_req.stop()

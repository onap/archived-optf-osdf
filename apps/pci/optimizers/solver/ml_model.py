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

import json

from osdf.adapters.dcae import des
from osdf.adapters.dcae.des import DESException
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import error_log


class MlModel(object):
    def __init__(self):
        self.config = osdf_config.core['PCI']

    def get_additional_inputs(self, dzn_data, network_cell_info):
        """Add/update additional info to the existing models.

        The method returns nothing. Instead, it modifies the dzn_data
        :params: dzn_data: map with data for the optimization
        """
        self.compute_ml_model(dzn_data, network_cell_info)

    def compute_ml_model(self, dzn_data, network_cell_info):
        average_ho_threshold = self.config['ML']['average_ho_threshold']
        latest_ho_threshold = self.config['ML']['latest_ho_threshold']

        fixed_cells = set()
        for cell in network_cell_info['cell_list']:
            cell_id = cell['cell_id']
            average_ho, latest_ho = self.get_ho_details(cell['cell_id'])
            if average_ho > average_ho_threshold or latest_ho > latest_ho_threshold:
                fixed_cells.add(cell_id)

        fixed_cells.update(dzn_data.get('PCI_UNCHANGEABLE_CELLS', []))
        dzn_data['PCI_UNCHANGEABLE_CELLS'] = fixed_cells

    def get_ho_details(self, cell_id):
        service_id = self.config['DES']['service_id']
        request_data = self.config['DES']['filter']
        request_data['cell_id'] = cell_id
        try:
            result = des.extract_data(service_id, json.dumps(request_data))
        except DESException as e:
            error_log.error("Error while calling DES {}".format(e))
            return 0, 0

        if not result:
            return 0, 0

        ho_list = []
        for pm_data in result:
            ho = pm_data['overallHoAtt']
            ho_list.append(ho)

        return sum(ho_list) / len(ho_list), ho_list[0]

# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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

from apps.pci.optimizers.config.config_client import ConfigClient
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import debug_log
from osdf.utils.interfaces import RestClient


@ConfigClient.register_subclass('cps')
class Cps(ConfigClient):

    def __init__(self):
        self.config = osdf_config.deployment
        username, password = self.config['cpsUsername'], self.config['cpsPassword']
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.rc = RestClient(userid=username, passwd=password, method="POST",
                             log_func=debug_log.debug, headers=headers)

    def get_cell_list(self, network_id):
        cell_list_url = '{}/{}'.format(self.config['cpsUrl'], self.config['cpsCellListUrl'])
        data = {
            'inputParameters': {
                'regionId': network_id
            }
        }
        response = self.rc.request(url=cell_list_url, data=json.dumps(data))
        debug_log.debug("cell list response {}".format(response))
        return sorted([x['idNRCellCU'] for x in response.get('NRCellCU')])

    def get_nbr_list(self, network_id, cell_id):
        nbr_list_url = '{}/{}'.format(self.config['cpsUrl'], self.config['cpsNbrListUrl'])
        data = {
            'inputParameters': {
                'regionId': network_id,
                'idNRCellCU': cell_id
            }
        }
        response = self.rc.request(url=nbr_list_url, data=json.dumps(data))
        debug_log.debug("nbr list response {}".format(response))
        nbr_list = []
        for cell_relation in response.get('NRCellRelation'):
            nbr = {
                'targetCellId': cell_relation['attributes']['nRTCI'],
                'pciValue': int(cell_relation['attributes']['nRPCI']),
                'ho': cell_relation['attributes']['isHOAllowed']
            }
            nbr_list.append(nbr)

        debug_log.debug("cell_id {} nbr_list {}".format(cell_id, nbr_list))

        return nbr_list

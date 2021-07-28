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

from datetime import datetime as dt
import uuid

from apps.pci.optimizers.config.config_client import ConfigClient
from osdf.config.base import osdf_config
from osdf.logging.osdf_logging import debug_log
from osdf.utils.interfaces import RestClient


@ConfigClient.register_subclass('configdb')
class ConfigDb(ConfigClient):

    def __init__(self):
        self.config = osdf_config.deployment
        uid, passwd = self.config['configDbUserName'], self.config['configDbPassword']
        headers = dict(transaction_id=str(uuid.uuid4()))
        self.rc = RestClient(userid=uid, passwd=passwd, method="GET", log_func=debug_log.debug, headers=headers)

    def get_cell_list(self, network_id):
        ts = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S%z')
        cell_list_url = '{}/{}/{}/{}'.format(self.config['configDbUrl'],
                                             self.config['configDbGetCellListUrl'], network_id, ts)
        return self.rc.request(raw_response=True, url=cell_list_url).json()

    def get_nbr_list(self, network_id, cell_id):
        ts = dt.strftime(dt.now(), '%Y-%m-%d %H:%M:%S%z')
        nbr_list_url = '{}/{}/{}/{}'.format(self.config['configDbUrl'],
                                            self.config['configDbGetNbrListUrl'], cell_id, ts)
        response = self.rc.request(url=nbr_list_url, raw_response=True).json()

        debug_log.debug("cell_id {} nbr_list {}".format(cell_id, response.get('nbrList')))

        return response.get('nbrList', [])

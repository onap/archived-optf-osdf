# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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

from apps.pci.optimizers.config.config_client import ConfigClient


def request(req_object, osdf_config, flat_policies):
    """Process a configdb request from a Client (build Conductor API call, make the call, return result)

    :param req_object: Request parameters from the client
    :param osdf_config: Configuration specific to OSDF application (core + deployment)
    :param flat_policies: policies related to PCI Opt (fetched based on request)
    :return: response from ConfigDB (accounting for redirects from Conductor service
    """
    cell_list_response = {}

    network_id = req_object['cellInfo']['networkId']

    cell_list_response['network_id'] = network_id

    config = osdf_config.deployment

    config_client = ConfigClient.create(config['configClientType'])

    cell_resp = config_client.get_cell_list(network_id)

    cell_list = []
    count = 0
    for cell_id in cell_resp:
        cell_info = {
            'cell_id': cell_id,
            'id': count,
            'nbr_list': config_client.get_nbr_list(network_id, cell_id)
        }
        cell_list.append(cell_info)
        count += 1

    cell_list_response['cell_list'] = cell_list

    return cell_resp, cell_list_response

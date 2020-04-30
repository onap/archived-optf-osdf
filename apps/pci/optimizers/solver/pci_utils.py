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

def mapping(network_cell_info):
    cell_id_mapping= dict()
    id_cell_mapping = dict()
    for i in network_cell_info['cell_list']:
        cell_id_mapping[i['cell_id']] = i['id']
        id_cell_mapping[i['id']] = i['cell_id']
    return cell_id_mapping, id_cell_mapping

def get_id(network_cell_info, cell_id):
    for i in network_cell_info['cell_list']:
        if i['cell_id'] == cell_id:
            return i['id']
    return None


def get_cell_id(network_cell_info, id):
    for i in network_cell_info['cell_list']:
        if i['id'] == id:
            return i['cell_id']
    return None


def get_pci_value(network_cell_info, id):
    cell_id = get_cell_id(network_cell_info, id)
    for i in network_cell_info['cell_list']:
        for j in i['nbr_list']:
            if cell_id == j['targetCellId']:
                return j['pciValue']
    return None

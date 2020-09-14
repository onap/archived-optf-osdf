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

from collections import defaultdict
import itertools
import os
import pymzn

from apps.pci.optimizers.solver.ml_model import MlModel
from apps.pci.optimizers.solver.pci_utils import get_id
from apps.pci.optimizers.solver.pci_utils import mapping

BASE_DIR = os.path.dirname(__file__)
cell_id_mapping = dict()
id_cell_mapping = dict()


def pci_optimize(network_cell_info, cell_info_list, request_json, osdf_config):
    global cell_id_mapping, id_cell_mapping
    cell_id_mapping, id_cell_mapping = mapping(network_cell_info)
    original_pcis = get_original_pci_list(network_cell_info)
    unchangeable_pcis = get_ids_of_fixed_pci_cells(request_json['cellInfo'].get('fixedPCICells', []))
    neighbor_edges = get_neighbor_list(network_cell_info)
    second_level_edges = get_second_level_neighbor(network_cell_info)
    ignorable_links = get_ignorable_links(network_cell_info, request_json)
    anr_flag = is_anr(request_json)

    dzn_data = build_dzn_data(cell_info_list, ignorable_links, neighbor_edges, second_level_edges, anr_flag,
                              original_pcis, unchangeable_pcis)

    ml_enabled = osdf_config.core['PCI']['ml_enabled']
    if ml_enabled:
        MlModel(osdf_config).get_additional_inputs(dzn_data, network_cell_info)

    return build_pci_solution(dzn_data, ignorable_links, anr_flag)


def get_ids_of_fixed_pci_cells(fixed_pci_list):
    fixed_pci_ids = set()
    for cell in fixed_pci_list:
        fixed_pci_ids.add(cell_id_mapping[cell])
    return fixed_pci_ids


def get_cell_id_pci_mapping(network_cell_info):
    original_pcis = dict()
    for cell in network_cell_info['cell_list']:
        for nbr in cell['nbr_list']:
            if cell_id_mapping[nbr['targetCellId']] not in original_pcis:
                original_pcis[cell_id_mapping[nbr['targetCellId']]] = nbr['pciValue']
    return original_pcis


def get_original_pci_list(network_cell_info):
    cell_id_pci_mapping = get_cell_id_pci_mapping(network_cell_info)
    original_pcis_list = []
    for i in range(len(cell_id_pci_mapping)):
        original_pcis_list.append(cell_id_pci_mapping.get(i))
    return original_pcis_list


def build_pci_solution(dzn_data, ignorable_links, anr_flag):
    mzn_solution = solve(get_mzn_model(anr_flag), dzn_data)
    if mzn_solution == 'UNSATISFIABLE':
        return mzn_solution
    solution = {'pci': mzn_solution[0]['pci']}

    if anr_flag:
        removables = defaultdict(list)
        used_ignorables = mzn_solution[0]['used_ignorables']
        index = 0
        for i in ignorable_links:
            if used_ignorables[index] > 0:
                removables[i[0]].append(i[1])
            index += 1
        solution['removables'] = removables
    return solution


def build_dzn_data(cell_info_list, ignorable_links, neighbor_edges, second_level_edges, anr_flag, original_pcis,
                   unchangeable_pcis):
    dzn_data = {
        'NUM_NODES': len(cell_info_list),
        'NUM_PCIS': len(cell_info_list),
        'NUM_NEIGHBORS': len(neighbor_edges),
        'NEIGHBORS': get_list(neighbor_edges),
        'NUM_SECOND_LEVEL_NEIGHBORS': len(second_level_edges),
        'SECOND_LEVEL_NEIGHBORS': get_list(second_level_edges),
        'PCI_UNCHANGEABLE_CELLS': unchangeable_pcis,
        'ORIGINAL_PCIS': original_pcis
    }
    if anr_flag:
        dzn_data['NUM_IGNORABLE_NEIGHBOR_LINKS'] = len(ignorable_links)
        dzn_data['IGNORABLE_NEIGHBOR_LINKS'] = get_list(ignorable_links)
    return dzn_data


def get_mzn_model(anr_flag):
    if anr_flag:
        mzn_model = os.path.join(BASE_DIR, 'min_confusion_inl.mzn')
    else:
        mzn_model = os.path.join(BASE_DIR, 'no_conflicts_no_confusion.mzn')
    return mzn_model


def is_anr(request_json):
    return 'pci-anr' in request_json["requestInfo"]["optimizers"]


def get_list(edge_list):
    array_list = []
    for s in edge_list:
        array_list.append([s[0], s[1]])
    return sorted(array_list)


def solve(mzn_model, dzn_data):
    return pymzn.minizinc(mzn=mzn_model, data=dzn_data)


def get_neighbor_list(network_cell_info):
    neighbor_list = set()
    for cell in network_cell_info['cell_list']:
        add_to_neighbor_list(network_cell_info, cell, neighbor_list)
    return neighbor_list


def add_to_neighbor_list(network_cell_info, cell, neighbor_list):
    for nbr in cell.get('nbr_list', []):
        host_id = cell['id']
        nbr_id = get_id(network_cell_info, nbr['targetCellId'])
        if nbr_id and host_id != nbr_id:
            neighbor_list.add((host_id, nbr_id))


def get_second_level_neighbor(network_cell_info):
    second_neighbor_list = set()
    for cell in network_cell_info['cell_list']:
        comb_list = build_second_level_list(network_cell_info, cell)
        for comb in comb_list:
            if comb[0] and comb[1]:
                second_neighbor_list.add((comb[0], comb[1]))
    return sorted(second_neighbor_list)


def build_second_level_list(network_cell_info, cell):
    second_nbr_list = []
    for nbr in cell.get('nbr_list', []):
        second_nbr_list.append(get_id(network_cell_info, nbr['targetCellId']))
    return [list(elem) for elem in list(itertools.combinations(second_nbr_list, 2))]


def get_ignorable_links(network_cell_info, request_json):
    ignorable_list = set()
    anr_input_list = request_json["cellInfo"].get('anrInputList', [])
    if anr_input_list:
        for anr_info in anr_input_list:
            cell_id = get_id(network_cell_info, anr_info['cellId'])
            anr_removable = anr_info.get('removeableNeighbors', [])
            for anr in anr_removable:
                ignorable_list.add((cell_id, get_id(network_cell_info, anr)))
    return ignorable_list

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

import itertools
import os

import pymzn

from .pci_utils import get_id

BASE_DIR = os.path.dirname(__file__)
MZN_FILE_NAME = os.path.join(BASE_DIR, 'no_conflicts_no_confusion.mzn')


def pci_optimize(network_cell_info, cell_info_list):
    neighbor_edges = get_neighbor_list(network_cell_info)
    second_level_edges = get_second_level_neighbor(network_cell_info)
    dzn_data = {
        'NUM_NODES': len(cell_info_list),
        'NUM_PCIS': len(cell_info_list),
        'NUM_NEIGHBORS': len(neighbor_edges),
        'NEIGHBORS': get_list(neighbor_edges),
        'NUM_SECOND_LEVEL_NEIGHBORS': len(second_level_edges),
        'SECOND_LEVEL_NEIGHBORS': get_list(second_level_edges)
    }

    return solve(dzn_data)


def get_list(edge_list):
    array_list = []
    for s in edge_list:
        array_list.append([s[0], s[1]])
    return sorted(array_list)


def solve(dzn_data):
    return pymzn.minizinc(MZN_FILE_NAME, data=dzn_data)


def get_neighbor_list(network_cell_info):
    neighbor_list = set()
    for cell in network_cell_info['cell_list']:
        add_to_neighbor_list(network_cell_info, cell, neighbor_list)
    return neighbor_list


def add_to_neighbor_list(network_cell_info, cell, neighbor_list):
    for nbr in cell.get('nbr_list', []):
        host_id = cell['id']
        nbr_id = get_id(network_cell_info, nbr['cellId'])
        if nbr_id and host_id != nbr_id:
            entry = sorted([host_id, nbr_id])
            neighbor_list.add((entry[0], entry[1]))


def get_second_level_neighbor(network_cell_info):
    second_neighbor_list = set()
    for cell in network_cell_info['cell_list']:
        comb_list = build_second_level_list(network_cell_info, cell)
        for comb in comb_list:
            if comb[0] and comb[1]:
                s = sorted(comb)
                second_neighbor_list.add((s[0], s[1]))
    return sorted(second_neighbor_list)


def build_second_level_list(network_cell_info, cell):
    second_nbr_list = []
    for nbr in cell.get('nbr_list', []):
        second_nbr_list.append(get_id(network_cell_info, nbr['cellId']))
    return [list(elem) for elem in list(itertools.combinations(second_nbr_list, 2))]

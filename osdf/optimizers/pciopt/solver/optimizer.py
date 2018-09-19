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

from osdf.logging.osdf_logging import debug_log
from .pci_utils import get_id

BASE_DIR = os.path.dirname(__file__)
MZN_FILE_NAME = os.path.join(BASE_DIR, 'no_conflicts_no_confusion.mzn')


def pci_optimize(cell_id, network_cell_info, cell_info_list):
    debug_log.debug("Cell ID {} ".format(cell_id))
    dzn_data = {}
    dzn_data['NUM_NODES'] = len(cell_info_list)
    dzn_data['NUM_PCIS'] = len(cell_info_list)

    conflict_edges = get_conflict_edges(cell_id, network_cell_info)

    dzn_data['NUM_CONFLICT_EDGES'] = len(conflict_edges)
    dzn_data['CONFLICT_EDGES'] = conflict_edges

    confusion_edges = get_confusion_edges(cell_id, network_cell_info)

    dzn_data['NUM_CONFUSION_EDGES'] = len(confusion_edges)
    dzn_data['CONFUSION_EDGES'] = confusion_edges

    return solve(dzn_data)

def solve(dzn_data):
    return pymzn.minizinc(MZN_FILE_NAME, data=dzn_data)


def get_conflict_edges(cell_id, network_cell_info):
    conflict_edges = []
    for cell in network_cell_info['cell_list']:

        if cell_id == cell['cell_id']:
            add_to_conflict_edges(network_cell_info, cell, conflict_edges)
    return conflict_edges


def add_to_conflict_edges(network_cell_info, cell, conflict_edges):
    cell_id = cell['cell_id']
    for nbr in cell.get('nbr_list', []):
        conflict_edges.append([get_id(network_cell_info, cell_id), get_id(network_cell_info, nbr['cellId'])])



def get_confusion_edges(cell_id, network_cell_info):
    confusion_edges = []
    for cell in network_cell_info['cell_list']:
        if cell_id == cell['cell_id']:
            return add_to_confusion_edges(network_cell_info, cell)
    return confusion_edges


def add_to_confusion_edges(network_cell_info, cell):
    cell_id = cell['cell_id']
    nbr_list = []
    for nbr in cell.get('nbr_list', []):
        nbr_list.append(get_id(network_cell_info, nbr['cellId']))
    return [list(elem) for elem in list(itertools.combinations(nbr_list, 2))]

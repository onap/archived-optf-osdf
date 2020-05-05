% -------------------------------------------------------------------------
%   Copyright (c) 2018 AT&T Intellectual Property
%
%   Licensed under the Apache License, Version 2.0 (the "License");
%   you may not use this file except in compliance with the License.
%   You may obtain a copy of the License at
%
%       http://www.apache.org/licenses/LICENSE-2.0
%
%   Unless required by applicable law or agreed to in writing, software
%   distributed under the License is distributed on an "AS IS" BASIS,
%   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
%   See the License for the specific language governing permissions and
%   limitations under the License.
%
% -------------------------------------------------------------------------
%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Parameters and its assertions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Number of cells/radios.
int: NUM_NODES;

% Maximum number of Physical Cell Identifiers to be assigned to the nodes.
int: NUM_PCIS;

% Number of edges between neighbor nodes. There is a edge (i,j) if and only
% if nodes i and j are neighbors, i.e., an user equipment (UE) can make
% handoff between i and j. Such edges are used to avoid **COLLISION**, i.e.,
% to guarantee that nodes i and j have different PCIs.
int: NUM_NEIGHBORS;

% Each line represents an edge between direct neighbors as defined before.
array[1..NUM_NEIGHBORS, 1..2] of int: NEIGHBORS;

% Number of undirect neighbor pairs (j, k) such that both j and k are direct
% neighbors of node i, i.e., (j, k) exits if and only if exists (i, j) and
% (i, k). Nodes (i, k) can generate "confunsions" in the network if they have
% the same PCI. Such edges are used to avoid/minimize **CONFUSIONS**.
int: NUM_SECOND_LEVEL_NEIGHBORS;

% Each line represents an edge between undirect neighbors as defined before.
array[1..NUM_SECOND_LEVEL_NEIGHBORS, 1..2] of int: SECOND_LEVEL_NEIGHBORS;

% Number of ignorable neighbor links. Such links can be ignored during
% optimization if needed.
int: NUM_IGNORABLE_NEIGHBOR_LINKS;

% The links that can be ignored if needed. Each line represents the two ends
% of the links, like the previous structures.
array[1..NUM_IGNORABLE_NEIGHBOR_LINKS, 1..2] of int: IGNORABLE_NEIGHBOR_LINKS;

% ids of cells for which the pci should remain unchanged
set of int: PCI_UNCHANGEABLE_CELLS;

% This array has the original pcis of all the cells. array is indexed by the ids
% of the cell. eg. ORIGINAL_PCIS[3] returns the pci of cell whose id is 3.
% ids start from 0
array[1..NUM_NODES] of 0..NUM_PCIS-1: ORIGINAL_PCIS;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Decision variables
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Defines the PCI for each node.
array[0..NUM_NODES-1] of var 0..NUM_PCIS-1: pci;

array[1..NUM_IGNORABLE_NEIGHBOR_LINKS] of var 0..1: used_ignorables;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Constraints
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% fixed pci cells
constraint
if(length(PCI_UNCHANGEABLE_CELLS) !=0) then
forall(i in PCI_UNCHANGEABLE_CELLS)(
    pci[i] == ORIGINAL_PCIS[i+1]
)
endif;

% Direct neighbors must have different PCIs for avoid **COLLISION**.
% Forced links.
constraint
forall(i in 1..NUM_NEIGHBORS, j in 1..NUM_IGNORABLE_NEIGHBOR_LINKS
    where
        NEIGHBORS[i, 1] != IGNORABLE_NEIGHBOR_LINKS[j, 1] \/
        NEIGHBORS[i, 2] != IGNORABLE_NEIGHBOR_LINKS[j, 2]
)(
    pci[NEIGHBORS[i, 1]] != pci[NEIGHBORS[i, 2]]
);


% Ignorable links.
constraint
forall(i in 1..NUM_NEIGHBORS, j in 1..NUM_IGNORABLE_NEIGHBOR_LINKS
    where
        NEIGHBORS[i, 1] == IGNORABLE_NEIGHBOR_LINKS[j, 1] /\
        NEIGHBORS[i, 2] == IGNORABLE_NEIGHBOR_LINKS[j, 2]
)(
    used_ignorables[j] >= bool2int(pci[NEIGHBORS[i, 1]] == pci[NEIGHBORS[i, 2]])
);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Objective function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Total number of confusions.
var int: total_confusions =
    sum([bool2int(pci[SECOND_LEVEL_NEIGHBORS[i, 1]] ==
                  pci[SECOND_LEVEL_NEIGHBORS[i, 2]])
         | i in 1..NUM_SECOND_LEVEL_NEIGHBORS]);

% Total number of used ignorables links.
var int: total_used_ignorables = sum(used_ignorables);

solve :: int_search(pci, smallest, indomain_min, complete)

% Minimize the total number of confusions.
%minimize total_confusions;

% Minimize the total number of confusions first,
% then the number of used ignorables links.
minimize (2 * NUM_IGNORABLE_NEIGHBOR_LINKS * total_confusions) +
         total_used_ignorables;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Output
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

output
["PCI assigment"] ++
["\nnode,pci"] ++
[
    "\n" ++ show(node) ++ "," ++ show(pci[node])
| node in 0..NUM_NODES-1
] ++
["\n\nTotal used ignorables links: " ++ show(total_used_ignorables)] ++
["\nUsed ignorables links: "] ++
[
    "\n" ++ show(IGNORABLE_NEIGHBOR_LINKS[i, 1]) ++
    ","  ++ show(IGNORABLE_NEIGHBOR_LINKS[i, 2])
    | i in 1..NUM_IGNORABLE_NEIGHBOR_LINKS where fix(used_ignorables[i] > 0)
] ++
["\n\nConfusions"] ++
["\nTotal confusions: " ++ show(total_confusions)] ++
["\nConfusion pairs"] ++
[
    "\n" ++ show(SECOND_LEVEL_NEIGHBORS[i, 1]) ++ "," ++
    show(SECOND_LEVEL_NEIGHBORS[i, 2])
    | i in 1..NUM_SECOND_LEVEL_NEIGHBORS where
      fix(pci[SECOND_LEVEL_NEIGHBORS[i, 1]] == pci[SECOND_LEVEL_NEIGHBORS[i, 2]])
]


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
% handoff between i and j. Such edges are used to avoid **CONFLICTS**, i.e.,
% to guarantee that nodes i and j have different PCIs.
int: NUM_CONFLICT_EDGES;

% Each line represents an edge between direct neighbors as defined before.
array[1..NUM_CONFLICT_EDGES, 1..2] of int: CONFLICT_EDGES; 

% Number of undirect neighbor pairs (j, k) such that both j and k are direct
% neighbors of node i, i.e., (j, k) exits if and only if exists (i, j) and 
% (i, k). Nodes (i, k) can generate "confunsions" in the network if they have
% the same PCI. Such edges are used to avoid/minimize **CONFUSIONS**.
int: NUM_CONFUSION_EDGES;

% Each line represents an edge between undirect neighbors as defined before.
array[1..NUM_CONFUSION_EDGES, 1..2] of int: CONFUSION_EDGES; 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Decision variables
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Defines the PCI for each node.
array[0..NUM_NODES-1] of var 0..NUM_PCIS-1: pci;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Constraints
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Direct neighbors must have different PCIs for avoid **CONFLICTS**.
constraint 
forall(i in 1..NUM_CONFLICT_EDGES)(
    pci[CONFLICT_EDGES[i, 1]] != pci[CONFLICT_EDGES[i, 2]]
);

% Undirect neighbors must have different PCIs for avoid **CONFUSIONS**.
constraint 
forall(i in 1..NUM_CONFUSION_EDGES)(
    pci[CONFUSION_EDGES[i, 1]] != pci[CONFUSION_EDGES[i, 2]]
);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Objective function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Just satisfy the problem.
solve :: int_search(pci, smallest, indomain_min, complete) satisfy;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Output
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

output
["node,pci\n"] ++
[
    show(node) ++ "," ++ show(pci[node]) ++ "\n"
| node in 0..NUM_NODES-1
]

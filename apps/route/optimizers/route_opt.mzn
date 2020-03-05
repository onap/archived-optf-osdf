
% Number of nodes
int: N;
    % Start node
0..N-1: Start;
    % End node
0..N-1: End;
    % Number of edges (directed arcs)
int: M;
    %  The actual edges
set of int: Edges = 1..M;
    % Edge lengths
array[Edges] of int: L;
    % Edge start node
array[Edges] of 0..N-1: Edge_Start;
array[Edges] of 0..N-1: Edge_End;

    % Variable indicating if edge is used
array[Edges] of var 0..1: x;

constraint
    forall( i in 0..N-1 ) (
        if i = Start then
                % outgoing flow
            sum(e in Edges where Edge_Start[e] = i)(x[e]) -
                % incoming flow
            sum(e in Edges where Edge_End[e] = i)(x[e])
            = 1
        elseif i = End then
            sum(e in Edges where Edge_Start[e] = i)(x[e]) -
            sum(e in Edges where Edge_End[e] = i)(x[e])
            = -1
        else
            sum(e in Edges where Edge_Start[e] = i)(x[e]) -
            sum(e in Edges where Edge_End[e] = i)(x[e])
            = 0
        endif
    );


solve minimize sum(e in Edges)( L[e] * x[e] );
%solve satisfy;

output ["Length: ", show(sum(e in Edges)(L[e] * x[e])), "\n"] ++
       ["Start : ", show(Start), "\n"] ++
       ["End   : ", show(End), "\n\n"] ++
       ["Edges in shortest path:\n"] ++
       [ if   fix(x[e]) = 1
         then show(Edge_Start[e]) ++ " -> " ++ show(Edge_End[e]) ++ "\n"
         else ""
         endif | e in Edges
       ];


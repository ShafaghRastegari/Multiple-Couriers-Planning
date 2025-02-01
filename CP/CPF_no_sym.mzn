include "globals.mzn";

/******************************************************************************
 *                              parameters                                    *
 ******************************************************************************/

int: m;
set of int: COURIERS = 1..m;      %set of couriers

int: n;
set of int: ITEMS = 1..n;           %set of items/locations

set of int: NODES = 1..n + 2*m;    %prepare for giant tour representation
set of int: START_NODES = n + 1..n + m;
set of int: END_NODES = n + m + 1..n + 2 * m;

array[COURIERS] of int: L; % maximum load size for each courier
set of int: LOADS = 0..max(L);

array[ITEMS] of int: S; % size of each item
array[NODES] of int: demand = [ 
 if i <= n then S[i] else 0 endif | i in NODES];

array[1..n+1, 1..n+1] of int: D; % distance matrix


int: upper_bound;
int: lower_bound;

/******************************************************************************
 *                              decision variables                            *
 ******************************************************************************/


array[NODES] of var NODES: successor;
array[NODES] of var NODES: predecessor;
array[NODES] of var COURIERS: route_m;
array[NODES] of var LOADS: load;
array[NODES] of var 0..upper_bound: final_dist;



/******************************************************************************
 *                              constraints                                  *
 ******************************************************************************/



% connect end nodes to the start nodes of next courier tour
constraint forall(i in n + m + 1..n + 2 * m - 1)(successor[i] = i - m + 1);
constraint successor[n + 2 * m] = n + 1;
constraint forall(i in n + 2..n + m)(predecessor[i] = i + m - 1);
constraint predecessor[n + 1] = n + 2 * m;
constraint forall(s in START_NODES)(not (successor[s] in END_NODES));

% assign each start->end nodes with a courier
constraint forall(i in START_NODES)(route_m[i] = i - n);
constraint forall(i in END_NODES)(route_m[i] = i - n - m);

%successor / predecessor consistency constraint 
constraint forall(i in NODES) (successor[predecessor[i]] == i);
constraint forall(i in NODES) (predecessor[successor[i]] == i);
constraint forall(i in ITEMS)(route_m[successor[i]] = route_m[i]);
constraint forall(i in ITEMS)(route_m[predecessor[i]] = route_m[i]);

% ensures each node is visited exactly once and create a complete tour 

constraint circuit(successor);


%distance travelled till each location 
% Initialize starting node of each route 
constraint forall(d in START_NODES)(final_dist[d] = 0);
constraint forall(d in ITEMS where successor[d] in ITEMS)(final_dist[successor[d]] = final_dist[d] + D[d,successor[d]]);
constraint forall(d in ITEMS where successor[d] in END_NODES)(final_dist[successor[d]] = final_dist[d] + D[d,n+1]);
constraint forall(d in START_NODES where successor[d] in ITEMS)(final_dist[successor[d]] = D[n+1, successor[d]]);
constraint forall(d in START_NODES where successor[d] in END_NODES)(final_dist[successor[d]] = 0);

%load and weight constraints 
constraint forall(i in START_NODES)(load[i] = 0);
constraint forall(i in ITEMS) (load[i] + demand[i] = load[successor[i]]);
constraint forall(i in START_NODES) (load[i] = load[successor[i]]);
constraint forall(i in ITEMS) (load[i] <= L[route_m[i]]);
constraint forall(i in COURIERS)(load[i + n + m] <= L[i]);

%Symmetry-breaking constraint

%constraint forall(i, j in COURIERS where i < j)(
%   (L[i] = L[j]) -> successor[n + i] < successor[n + j]
%);
/******************************************************************************
 *                              search and solve                                  *
 ******************************************************************************/
var lower_bound..upper_bound: obj;
constraint obj = max(final_dist);

%solve minimize obj;


solve :: seq_search([
    int_search(successor, first_fail, indomain_split),
    int_search(load, first_fail, indomain_split),
    int_search(route_m, first_fail, indomain_split)
]) minimize(obj)::domain

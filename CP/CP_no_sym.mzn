include "globals.mzn";

/******************************************************************************
 *                              parameters                                    *
 ******************************************************************************/

int: m;
set of int: COURIERS = 1..m;      %set of couriers

int: n;
set of int: ITEMS = 1..n;           %set of customers/locations

set of int: NODES = 1..n + 2*m;    %prepare for giant tour representation
set of int: START_NODES = n + 1..n + m;
set of int: END_NODES = n + m + 1..n + 2 * m;

array[COURIERS] of int: L; % maximum load size for each courier
set of int: LOADS = 0..max(L);

array[ITEMS] of int: S; % size of each item
array[NODES] of int: demand = [ 
 if i <= n then S[i] else 0 endif | i in NODES];

array[1..n+1, 1..n+1] of int: D; % distance matrix


int: low_bound = max(i in ITEMS)(D[n+1,i] + D[i,n+1]); % lower bound for objective function
int: S_min = min(j in ITEMS)(S[j]);
int: K_max = max(i in COURIERS)(floor(L[i] / S_min));
int: D_max_origin = max(j in ITEMS)(D[n+1, j]);
int: D_max = max(i in ITEMS, j in ITEMS where i != j)(D[i, j]);
int: up_bound = 2 * D_max_origin + (K_max - 1) * D_max ; % upper bound for objective function

/******************************************************************************
 *                              decision variables                            *
 ******************************************************************************/


array[NODES] of var NODES: successor;
array[NODES] of var NODES: predecessor;
array[NODES] of var COURIERS: courier_route;
array[NODES] of var LOADS: load;
array[NODES] of var 0..up_bound: final_dist;



/******************************************************************************
 *                              constraints                                  *
 ******************************************************************************/



% connect end nodes to the start nodes of next courier tour
constraint forall(i in n + m + 1..n + 2 * m - 1)(successor[i] = i - m + 1);
constraint successor[n + 2 * m] = n + 1;
constraint forall(i in n + 2..n + m)(predecessor[i] = i + m - 1);
constraint predecessor[n + 1] = n + 2 * m;
% assign each start->end nodes with a courier
constraint forall(i in START_NODES)(courier_route[i] = i - n);
constraint forall(i in END_NODES)(courier_route[i] = i - n - m);

%successor / predecessor consistency constraint 
constraint forall(i in NODES) ((successor[predecessor[i]] == i) /\ (predecessor[successor[i]] == i));

constraint forall(i in ITEMS)(courier_route[successor[i]] = courier_route[i]);
constraint forall(i in ITEMS)(courier_route[predecessor[i]] = courier_route[i]);

/* --- Ensures each node is visited exactly once--- */
/* --- Creates a complete tour without subtours--- */

constraint circuit(successor) /\ circuit(predecessor);

/* --- --- */
constraint forall(i in START_NODES)(final_dist[i] = 0);
constraint forall(i in START_NODES)(final_dist[successor[i]] = D[n + 1, successor[i]]);   % dep->successor[i]
constraint forall(i in ITEMS)(final_dist[successor[i]] = final_dist[i] + D[i, min([successor[i], n+1])]);


/* ---load and weight constraints--- */
constraint forall(i in START_NODES)(load[i] = 0);
constraint forall(i in ITEMS) (load[i] + demand[i] = load[successor[i]]);
constraint forall(i in START_NODES) (load[i] = load[successor[i]]);
constraint forall(i in ITEMS) (load[i] <= L[courier_route[i]]);
constraint forall(i in COURIERS)(load[i + n + m] <= L[i]);

/* ---Symmetry-breaking constraint---*/

%constraint forall(i, j in COURIERS where i < j)(
%   (L[i] >= L[j] /\ L[j] >= L[i]) -> successor[n + i] < successor[n + j]
%);
/******************************************************************************
 *                              search and solve                                  *
 ******************************************************************************/
var low_bound..up_bound: obj;
constraint obj = max(final_dist);

%solve minimize obj;

solve :: seq_search([
               int_search(successor, first_fail, indomain_split),
               int_search(predecessor, first_fail, indomain_split),
               int_search(load, first_fail, indomain_split),
               int_search(courier_route, first_fail, indomain_split)
               
               
             
]) minimize(obj)::domain;

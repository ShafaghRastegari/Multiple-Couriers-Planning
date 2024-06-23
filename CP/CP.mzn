% Data
int: m; % Number of couriers
int: n; % Number of items
array[1..m] of int: l; % Maximum load capacity for each courier
array[1..n] of int: s; % Size of each item
array[1..n+1, 1..n+1] of int: D; % Distance matrix, with origin as the last point

output ["m = ", show(m), "\n", 
        "n = ", show(n), "\n", 
        "l = ", show(l), "\n", 
        "s = ", show(s), "\n", 
        "D = ", show(D), "\n"];
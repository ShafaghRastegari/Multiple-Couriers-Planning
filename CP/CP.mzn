int: m; % Number of couriers
int: n; % Number of items
array[1..m] of int: L; % Maximum load of each courier
array[1..n] of int: S; % Size of each item
array[1..n+1, 1..n+1] of int: D; % Distance matrix

% Decision variable: courier k travels from i to j
array[1..m, 0..n+1, 0..n+1] of var 0..1: x;
% Load for each courier
array[1..m] of var int: load;

%%%%%%%%%%%%% Constraints %%%%%%%%%%%%%

% Each item should delivered
constraint
  forall(i in 1..n) (
    sum(k in 1..m, j in 1..n+1)(x[k,i,j]) = 1
);

% Couriers does not pass their max load
constraint
  forall(k in 1..m) (
    (load[k] == sum(i in 1..n, j in 1..n+1 where x[k,i,j] = 1)(S[i]))/\
    (load[k] <= L[k])
   );
   
% For each courier that have item it should not return to itself
% It should start and end at n+1 
constraint
  forall(k in 1..m) (
    ((count(i in 1..n, j in 1..n+1)(x[k,i,j] = 1) > 0) -> (forall(i in 1..n+1)(x[k,i,i]=0) /\                
        sum(j in 1..n)(x[k,n+1,j]) = 1 /\ sum(i in 1..n)(x[k,i,n+1]) = 1))
        );
 
constraint forall(k in 1..m, i in 1..n+1, j in 1..n+1 where i != j) (
    x[k,i,j] = 1 -> x[k,j,i] = 0
);


constraint
  forall(k in 1..m, h in 1..n) (
    (sum(i in 1..n+1)(x[k,i,h]) - sum(j in 1..n+1)(x[k,h,j]))=0);
    
%%%%%%%%%%%%% Symmetry Breaking %%%%%%%%%%%%%


% Define lowerbound
int: obj_lowerbound = max(i in 1..n)(D[n+1,i] + D[i,n+1]);
array[1..n] of int: max_dists = sort([max(j in 1..n)(D[i,j]) | i in 1..n]);

% Define uperbound
int: obj_upperbound = sum(i in m+1..n)(max_dists[i]) + max(j in 1..n)(D[n+1,j]) + max(j in 1..n)(D[j,n+1]);
        
var obj_lowerbound..obj_upperbound: obj = max(k in 1..m)(sum(i,j in 1..n+1 where x[k,i,j] = 1) (D[i,j]));


% Minimize the objective fuction: Minimize the total distance traveled
solve minimize obj;

%Output
output [
    show(obj) ++ "\n"
] ++
[
    show(x[k, i, j]) ++ if j == n+1 then "\n" else " " endif
    | k in 1..m, i in 1..n+1, j in 1..n+1
];
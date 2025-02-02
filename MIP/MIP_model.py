from utils import *
from pulp import *

def solve_mip(m, n, L, S, D):
    
    model = LpProblem("Multiple_Couriers_Planning", LpMinimize)
    
    # Decision Variables
    x = LpVariable.dicts("x", (range(m), range(n+1), range(n+1)), cat='Binary')
    a = LpVariable.dicts("a", (range(m), range(n)), cat="Binary")
    t = LpVariable.dicts("t", (range(m), range(n)), lowBound=0, upBound=n, cat="Integer")
    

    upper_bound = calculate_upper_bound(m, n, L, S, D)
    lower_bound = calculate_lower_bound(n, D)

    max_distance = LpVariable("max_distance", lowBound=lower_bound, upBound=upper_bound, cat="Integer")
    
    courier_weights = [
        LpVariable(name=f'weight_{i}', lowBound=0, upBound=L[i], cat="Integer")
        for i in range(m)
    ]
    
    courier_distance = [
        LpVariable(name=f'obj_dist{i}', cat="Integer", lowBound=0, upBound=upper_bound)
        for i in range(m)
    ]
    
    # Objective Function
    model += max_distance
    
    # Constraints

    # The constraint ensures this value is less than or equal to the courier's capacity
    for k in range(m):
        model += lpSum([S[j] * a[k][j] for j in range(n)]) == courier_weights[k]
     
    # No self-loops(courier traveling from a city to itself)
    for k in range(m):
        model += lpSum(x[k][i][i] for i in range(n)) == 0
            
    # Every item must be delivered by exactly one courier 
    # and ensures every node, except the depot, is entered just once
    for j in range(n):
        model += lpSum(a[k][j] for k in range(m)) == 1 
        model += lpSum(x[k][i][j] for i in range(n+1) for k in range(m)) == 1 
   
    # Ensures every courier leaves exactly once from the depot.
    for k in range(m):
        model += lpSum(x[k][n]) == 1  # Start from depot exactly once
        model += lpSum(x[k][j][n] for j in range(n+1)) == 1  # End at the depot
    
    # if courier k delivered item j thats mean the courier k should leave the item j
    for k in range(m):
        for j in range(n):
            model += lpSum(x[k][j]) == a[k][j]    
    
    # the number of the input and output for an item must be equal (except depot)
    for j in range(n):
        for k in range(m):
            model += lpSum(x[k][i][j] for i in range(n+1)) == lpSum(x[k][j])
            
    # remove loop on items-courier k delivered one of the j-i or i-j or none of them
    for k in range(m):
        for i in range(n):
            for j in range(n):
                model += (x[k][i][j]   + x[k][j][i])  <= 1
    
    
    # MTZ subtour elimination
    for k in range(m):
        for i in range(n):
            for j in range(n):
                if i != j:
                    model += (t[k][i] - t[k][j])  <= (n) * (1 - x[k][i][j]) - 1

    for k in range(m):
        model += lpSum([D[i][j] * x[k][i][j] for i in range(n+1) for j in range(n+1)]) == courier_distance[k]
        
    # Ensure max_distance is at least as large as the longest courier distance
    for k in range(m):
        model += max_distance >= courier_distance[k]
        
    return model, x, max_distance
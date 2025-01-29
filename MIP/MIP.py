from pulp import *
import time
import os
import json
from utils import calculate_lower_bound, calculate_upper_bound


def read_mcp_instance(filename):
    with open(filename, 'r') as f:
        # number of couriers
        m = int(f.readline())

        # number of items
        n = int(f.readline())
        
        # Read courier load capacities
        loads = list(map(int, f.readline().split()))
        
        # Read item sizes
        sizes = list(map(int, f.readline().split()))
        
        # Read distance matrix
        distances = []
        for _ in range(n + 1):  # n items + origin point
            row = list(map(int, f.readline().split()))
            distances.append(row)
            
    return m, n, loads, sizes, distances

def solve_mcp(m, n, L, S, D, solver):
    
    start_time = time.time()
    model = LpProblem("Multiple_Couriers_Planning", LpMinimize)
    
    K = range(m)  # Couriers
    N = range(n)  # Items
    N0 = range(n + 1)  # Items + depot
    
    # Decision Variables
    """
    Xijk = 1 If there is a path
         = 0 If there is not a path
    """
    x = LpVariable.dicts("x", [(i, j, k) for i in N0 for j in N0 for k in K], cat='Binary')
    u = LpVariable.dicts("u", [(i,k) for i in N for k in K], lowBound=0, upBound=n-1)

    upper_bound = calculate_upper_bound(m, n, L, S, D)
    lower_bound = calculate_lower_bound(n, D)

    max_distance = LpVariable("max_distance", lowBound=lower_bound, upBound=upper_bound)
    
    courier_weights = [
        LpVariable(name=f'weight_{i}', lowBound=0, upBound=L[i], cat="Integer")
        for i in K
    ]
    
    courier_distance = [
        LpVariable(name=f'obj_dist{i}', cat="Integer", lowBound=lower_bound, upBound=upper_bound)
        for i in K
    ]
    
    # Objective Function
    model += max_distance
    
    # Constraints
    
    # 1. Ensure flow conservation at all nodes (except depot)
    for h in N:
        for k in K:
            model += lpSum(x[i, h, k] for i in N0 if i != h) == lpSum(x[h, j, k] for j in N0 if j != h)

    # 2. Every item must be delivered by exactly one courier 
    # and ensures every node, except the depot, is entered just once
    for i in N:
        model += lpSum(x[i,j,k] for j in N0 for k in K) == 1
    
    # 3. Ensures every courier leaves exactly once from the depot.
    for k in K:
        model += lpSum(x[n, j, k] for j in N) == 1  # Start from depot exactly once

    # # 4. The constraint ensures this value is less than or equal to the courier's capacity
    for k in K:
        model += lpSum(S[i] * lpSum(x[i,j,k] for j in N0) for i in N) <= L[k]
    
    # 5. each courier returns to the depot exactly once
    for k in K:
        model += lpSum(x[i, n, k] for i in N) == 1  # End at the depot
    
    # 6. No self-loops(courier traveling from a city to itself)
    for i in N0:
        for k in K:
            model += x[i,i,k] == 0

    # 7. Ensure max_distance is at least as large as the longest courier distance
    for k in K:
        model += max_distance >= courier_distance[k]
    
    # 8. MTZ subtour elimination
    for i in N:
        for j in N:
            if i != j:
                for k in K:
                    model += u[(i, k)] - u[(j, k)] + n * x[i, j, k] <= n - 1

    # # 9.
    # # Set weight carried by each courier
    # for k in K:
    #     model += courier_weights[k] == lpSum(S[i] * lpSum(x[i, j, k] for j in N0) for i in N)

    # Set the total travel distance for each courier
    for k in K:
        model += courier_distance[k] == lpSum(D[i][j] * x[i, j, k] for i in N0 for j in N0)

    # Ensure couriers respect their weight capacities
    for k in K:
        model += courier_weights[k] <= L[k]  # Each courier must not exceed its weight limit

    # # Ensure each courier's traveled distance is within its range
    # for k in K:
    #     model += courier_distance[k] <= upper_bound


    model.solve(solver)

    # End timing
    end_time = time.time()
    running_time = end_time - start_time
    
    # Extract solution
    if model.status == LpStatusOptimal:
        routes = {}
        for k in K:
            route = []
            current = n
            while True:
                next_point = None
                for j in N0:
                    if value(x[current, j, k]) > 0.5:
                        next_point = j
                        break  # Exit the loop once a valid `next_point` is found
                if next_point is None or next_point == n:  # Back to depot or no next point
                    #route.append("Depot")  # Mark depot explicitly
                    break
                else:
                    route.append(next_point + 1)  # Convert item indices to 1-based
                    current = next_point

            if route:  # Only include routes that are used
                routes[k] = route
        
        return {
            'status': 'true',
            'objective': value(max_distance),
            'routes': routes.values(),
            'running_time': running_time
        }
    else:
        return {
            'status': 'false',
            'objective': None,
            'routes': {},
            'running_time': running_time
        }
        
        
        
def save_solution_to_json(instance_name, solver_name, solution, output_folder="res/MIP"):
    
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{instance_name}.json")
    
    if os.path.exists(output_file):
        with open(output_file, 'r') as json_file:
            json_data = json.load(json_file)
    else:
        json_data = {}
    
    json_data[solver_name] = {
        "time": int(solution['running_time']),
        "optimal": solution['status'],
        "obj": int(solution.get("objective", 0)) if solution.get("objective") is not None else None,
        "sol": list(solution['routes']),
    }
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Solution for {solver_name} saved to {output_file}")
    
    
    
def usage():
    solvers = {
        "PULP_CBC_CMD": PULP_CBC_CMD(msg=False, timeLimit=300),
        "GUROBI": GUROBI(msg=False, timeLimit=300),
        "HiGHS": getSolver('HiGHS', timeLimit=300, msg=False)
    }

    for instance_num in range(0,5):
        print(f"instance : {instance_num + 1}")
        instance_file = f"Instances/inst0{instance_num+1}.dat" if instance_num < 9 else f"Instances/inst{instance_num+1}.dat"
        instance_name = instance_num + 1
        output_file = "result/MIP"
    
        m, n, L, S, D = read_mcp_instance(instance_file)

        for solver_name, solver in solvers.items():
            solution = solve_mcp(m, n, L, S, D, solver)
            save_solution_to_json(instance_name, solver_name, solution, output_file)


if __name__ == "__main__":
    usage()

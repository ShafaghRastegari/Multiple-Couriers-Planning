from pulp import *
import time
import os
import json
import numpy as np
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
        #distances = np.array([list(map(int, f.readline().split())) for line in lines[4:]])
            
    return m, n, loads, sizes, distances

def solve_mcp(m, n, L, S, D, solver):
    
    start_time = time.time()
    model = LpProblem("Multiple_Couriers_Planning", LpMinimize)
    
    num_couriers = m  # Couriers
    N = n  # Items
    N0 = n + 1  # Items + depot
    
    origin = len(D[1])
    num_cities = len(D[1])-1 #except depot
    
    # Decision Variables
    """
    Xijk = 1 If there is a path
         = 0 If there is not a path
    """
    x = LpVariable.dicts("x", (range(origin), range(origin), range(num_couriers)), cat='Binary')
    u = LpVariable.dicts("u", (range(num_cities), range(num_couriers)), lowBound=0, upBound=origin-1, cat="Integer")

    upper_bound = calculate_upper_bound(m, n, L, S, D)
    lower_bound = calculate_lower_bound(n, D)

    max_distance = LpVariable("max_distance", lowBound=lower_bound, upBound=upper_bound, cat="Integer")
    
    courier_weights = [
        LpVariable(name=f'weight_{i}', lowBound=0, upBound=L[i], cat="Integer")
        for i in range(num_couriers)
    ]
    
    courier_distance = [
        LpVariable(name=f'obj_dist{i}', cat="Integer", lowBound=min(D[i][n]+D[n][i] for i in range(n)), upBound=upper_bound)
        for i in range(num_couriers)
    ]
    
    # Objective Function
    model += max_distance
    
    # Constraints

     # # 4. The constraint ensures this value is less than or equal to the courier's capacity
    for k in range(num_couriers):
        model += lpSum([S[j] * x[i][j][k] for j in range(num_cities) for i in range(origin)]) == courier_weights[k]
     
    # 6. No self-loops(courier traveling from a city to itself)
    for k in range(num_couriers):
        model += lpSum(x[i][i][k] for i in range(origin)) == 0
            
    # 2. Every item must be delivered by exactly one courier 
    # and ensures every node, except the depot, is entered just once
    for j in range(num_cities):
        model += lpSum(x[i][j][k] for i in range(origin) for k in range(num_couriers)) == 1 
   
     
     # 3. Ensures every courier leaves exactly once from the depot.
    for k in range(num_couriers):
        model += lpSum(x[num_cities][j][k] for j in range(num_cities)) == 1  # Start from depot exactly once

        
    # 5. each courier returns to the depot exactly once
    for k in range(num_couriers):
        model += lpSum(x[i][num_cities][k] for i in range(num_cities)) == 1  # End at the depot
    
    
    # 1. Ensure flow conservation at all nodes (except depot)
    for h in range(origin):
        for k in range(num_couriers):
            model += lpSum(x[i][h][k] for i in range(origin) if i != h) == lpSum(x[h][j][k] for j in range(origin) if j != h)
    
    
    # 8. MTZ subtour elimination
    for k in range(num_couriers):
        for i in range(num_cities):
            for j in range(num_cities):
                if i != j:
                    model += (u[i][k] - u[j][k]) + ((num_cities + 1) * x[i][j][k]) <= num_cities-1


    for k in range(num_couriers):
        model += lpSum([D[i][j] * x[i][j][k] for i in range(origin) for j in range(origin)]) == courier_distance[k]
        
    # 7. Ensure max_distance is at least as large as the longest courier distance
    for k in range(num_couriers):
        model += max_distance >= courier_distance[k]


    model.solve(solver)

    # End timing
    end_time = time.time()
    running_time = end_time - start_time

    # Extract solution

    if model.status == LpStatusOptimal:
        routes = {}
        for k in range(num_couriers):
            route = []
            current = n
            while True:
                next_point = None
                for j in range(N0):
                    if value(x[current][j][k]) > 0.5:
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
        
        
def pathFormatter(x, n_cities, n_couriers):
    """
    Formats paths for each courier based on the assignment matrix.

    Parameters:
        x (dict): The decision variables representing whether courier c travels from city i to city j.
        n_cities (int): The total number of cities, including the depot.
        n_couriers (int): The total number of couriers.

    Returns:
        list: A list of lists, where each inner list contains the sequence of city indices (1-based) 
              representing the route for each courier.
    """
    sol = []
    for c in range(n_couriers):
        solution_courier = []
        # Count the number of cities assigned to this courier.
        num_assigned_to_courier = len([1 for i in range(n_cities) for j in range(n_cities) if value(x[i][j][c]) >= 0.9])
        
        # Find the starting city for this courier (first city after leaving the depot).
        for i in range(n_cities - 1):  # Exclude the depot.
            if value(x[n_cities - 1][i][c]) >= 0.9:
                solution_courier.append(i + 1)  # Convert to 1-based index.
                city = i
                break
        
        # Trace the path for all assigned cities except the starting city.
        for _ in range(num_assigned_to_courier - 1):
            for i in range(n_cities - 1):  # Exclude the depot.
                if value(x[city][i][c]) > 0.9:
                    solution_courier.append(i + 1)  # Convert to 1-based index.
                    city = i
                    break
        
        sol.append(solution_courier)
    return sol
    
    '''    
    if model.status == LpStatusOptimal:
        routes = {}
        for k in range(num_couriers):
            route = []
            current = n  # Start at the depot
            max_iterations = N0  # Maximum number of iterations
            iteration_count = 0

            while True:
                iteration_count += 1
                if iteration_count > max_iterations:
                    raise RuntimeError("Infinite loop detected in route extraction.")

                next_point = None
                for j in range(N0):
                    if value(x[current][j][k]) >= 0.9:  # Use the same threshold as format_paths
                        next_point = j
                        break

                if next_point is None or next_point == n:
                    route.append("Depot")  # Mark depot explicitly
                    break
                elif next_point < 0 or next_point >= N0:
                    raise ValueError(f"Invalid next_point index: {next_point}")
                else:
                    route.append(next_point + 1)  # Convert item indices to 1-based
                    current = next_point

            if not route:
                route = ["Unused"]  # Mark unused couriers
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
    '''
        
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
        #"GUROBI": GUROBI(msg=False, timeLimit=300),
        "HiGHS": getSolver('HiGHS', timeLimit=300, msg=False)
    }

    for instance_num in range(11,21):
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

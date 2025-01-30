from pulp import *
import time
import os
import json
import numpy as np
from utils import calculate_lower_bound, calculate_upper_bound
import multiprocessing as mp


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
    x = LpVariable.dicts("x", (range(m), range(n+1), range(n+1)), cat='Binary')
    a = LpVariable.dicts("a", (range(m), range(n)), cat="Binary")
    t = LpVariable.dicts("t", (range(m), range(n)), lowBound=0, upBound=n, cat="Integer")
    

    upper_bound = calculate_upper_bound(m, n, L, S, D)
    lower_bound = calculate_lower_bound(n, D)

    max_distance = LpVariable("max_distance", lowBound=lower_bound, upBound=upper_bound, cat="Integer")
    
    courier_weights = [
        LpVariable(name=f'weight_{i}', lowBound=0, upBound=L[i], cat="Integer")
        for i in range(num_couriers)
    ]
    
    courier_distance = [
        LpVariable(name=f'obj_dist{i}', cat="Integer", lowBound=0, upBound=upper_bound)
        for i in range(num_couriers)
    ]
    
    # Objective Function
    model += max_distance
    
    # Constraints

     # # 4. The constraint ensures this value is less than or equal to the courier's capacity
    for k in range(m):
        model += lpSum([S[j] * a[k][j] for j in range(n)]) == courier_weights[k]
     
    # 6. No self-loops(courier traveling from a city to itself)
    for k in range(m):
        model += lpSum(x[k][i][i] for i in range(n)) == 0
            
    # 2. Every item must be delivered by exactly one courier 
    # and ensures every node, except the depot, is entered just once
    for j in range(n):
        model += lpSum(a[k][j] for k in range(m)) == 1 
        model += lpSum(x[k][i][j] for i in range(n+1) for k in range(m)) == 1 
        
        #model += lpSum(x[k][j][i] for i in range(n+1) for k in range(m)) == 1 
   
     
     # 3. Ensures every courier leaves exactly once from the depot.
    for k in range(m):
        model += lpSum(x[k][n]) == 1  # Start from depot exactly once
        model += lpSum(x[k][j][n] for j in range(n+1)) == 1  # End at the depot
    
    for k in range(m):
        for j in range(n):
            model += lpSum(x[k][j]) == a[k][j]
        
    # 5. each courier returns to the depot exactly once
    #for k in range(num_couriers):
     #   model += lpSum(x[i][num_cities][k] for i in range(num_cities)) == 1  # End at the depot
    
    
    # 1. Ensure flow conservation at all nodes (except depot)
    for j in range(n):
        for k in range(m):
            model += lpSum(x[k][i][j] for i in range(n+1)) == lpSum(x[k][j])
            
    for k in range(m):
        for i in range(n):
            for j in range(n):
                model += (x[k][i][j]   + x[k][j][i])  <= 1
    
    
    # 8. MTZ subtour elimination
    for k in range(m):
        for i in range(n):
            for j in range(n):
                if i != j:
                    model += (t[k][i] - t[k][j])  <= (n) * (1 - x[k][i][j]) - 1
                    #model += (t[k][j] - t[k][i])  <= (n+2) * (1 - x[k][i][j]) - 1


    for k in range(m):
        model += lpSum([D[i][j] * x[k][i][j] for i in range(n+1) for j in range(n+1)]) == courier_distance[k]
        
    # 7. Ensure max_distance is at least as large as the longest courier distance
    for k in range(m):
        model += max_distance >= courier_distance[k]


    model.solve(solver)
    # for var in model.variables():
    #    print(f"{var.name} = {var.varValue}")

    # End timing
    end_time = time.time()
    running_time = end_time - start_time

    # Extract solution

    if model.status == LpStatusOptimal:
        routes = {}
        for k in range(m):
            route = []
            current = n
            while True:
                next_point = None
                for j in range(N0):
                    if value(x[k][j][current]) > 0.9:
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
    
    import multiprocessing as mp

def solve_and_save(m, n, L, S, D, solver, instance_name, solver_name, output_file):
    """
    Wrapper function to solve the model and save the solution.
    """
    solution = solve_mcp(m, n, L, S, D, solver)
    save_solution_to_json(instance_name, solver_name, solution, output_file)

def usage():
    solvers = {
        "PULP_CBC_CMD": PULP_CBC_CMD(msg=False, timeLimit=300),
        "GUROBI": GUROBI(timeLimit=300, msg=False),
        "HiGHS": getSolver('HiGHS', timeLimit=300, msg=False)
    }

    for instance_num in range(10, 21):
        print(f"instance : {instance_num + 1}")
        instance_file = f"Instances/inst0{instance_num+1}.dat" if instance_num < 9 else f"Instances/inst{instance_num+1}.dat"
        instance_name = instance_num + 1
        output_file = "result/MIP"
    
        m, n, L, S, D = read_mcp_instance(instance_file)

        # Create a list to hold all processes
        processes = []

        for solver_name, solver in solvers.items():
            # Create a process for each solver
            process = mp.Process(
                target=solve_and_save,
                args=(m, n, L, S, D, solver, instance_name, solver_name, output_file)
            )
            processes.append(process)
            process.start()  # Start the solver in a separate process

        # Wait for all processes to complete or timeout
        for process in processes:
            process.join(timeout=300)  # Wait for the process to complete or timeout

            if process.is_alive():
                # Solver exceeded the time limit
                process.terminate()  # Force terminate the solver
                process.join()  # Ensure the process is cleaned up

                solution_data = {
                    'status': 'false',
                    'objective': None,
                    'routes': {},
                    'running_time': 300
                }
                save_solution_to_json(instance_name, solver_name, solution_data, output_file)

'''   
def usage():
    solvers = {
        #"PULP_CBC_CMD": PULP_CBC_CMD(msg=False, timeLimit=300),
        "GUROBI": GUROBI(timeLimit=300, msg=False)
        #"HiGHS": getSolver('HiGHS', timeLimit=300, msg=False)
    }

    for instance_num in range(1,5):
        print(f"instance : {instance_num + 1}")
        instance_file = f"Instances/inst0{instance_num+1}.dat" if instance_num < 9 else f"Instances/inst{instance_num+1}.dat"
        instance_name = instance_num + 1
        output_file = "result/MIP"
    
        m, n, L, S, D = read_mcp_instance(instance_file)

        for solver_name, solver in solvers.items():
            
            
            process = mp.Process(target=solver_name)
            process.start()  # Start the solver in a separate process
            process.join(timeout = 300)  # Wait for the process to complete or timeout
            
            
            
            solution = solve_mcp(m, n, L, S, D, solver)
            
            save_solution_to_json(instance_name, solver_name, solution, output_file)
'''

if __name__ == "__main__":
    usage()

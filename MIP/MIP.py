from pulp import *
import time
import os
import json
import numpy as np
import multiprocessing as mp
from MIP.MIP_model import solve_mip


def read_mcp_instance(filename):
    with open(filename, 'r') as f:
        m = int(f.readline())
        n = int(f.readline())
        loads = list(map(int, f.readline().split()))
        sizes = list(map(int, f.readline().split()))
        distances = []
        for _ in range(n + 1):  # n items + origin point
            row = list(map(int, f.readline().split()))
            distances.append(row)
            
    return m, n, loads, sizes, distances


def solve_model(model, m, n, x, max_distance, solver):

    model.solve(solver)
    if model.status == 1:
        routes = {}
        for k in range(m):
            route = []
            current = n
            while True:
                next_point = None
                for j in range(n+1):
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
            'time': int(model.solutionTime),
            'optimal': True,
            'obj': round(value(max_distance)),
            'sol': list(routes.values())
        }
    else:
        return {
            'time': 300,
            'optimal': False,
            'obj': "N/A",
            'sol': []
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
        "time": solution['time'],
        "optimal": solution['optimal'],
        "obj": solution["obj"],
        "sol": solution['sol'],
    }
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Solution for {solver_name} saved to {output_file}")


def solve_and_save(shared_list, m, n, L, S, D, solver):
    model, x, max_distance = solve_mip(m, n, L, S, D)
    solution = solve_model(model, m, n, x, max_distance, solver)
    shared_list.append((solution['time'], solution['optimal'], solution['obj'], solution['sol']))
    

def run_model(num_instance):
    if num_instance == 0:
        start = 10
        end = 21
    else:
        start = num_instance - 1
        end = num_instance
    
    solvers = {
        "PULP_CBC_CMD": PULP_CBC_CMD(msg=False, timeLimit=300),
        "GUROBI": GUROBI(timeLimit=300, msg=False),
        "HiGHS": getSolver('HiGHS', timeLimit=300, msg=False)
    }

    for instance_num in range(start, end):
        print(f"instance : {instance_num + 1}")
        instance_file = os.path.join(".", "Instances", f"inst0{instance_num+1}.dat") if instance_num < 9 else os.path.join(".", "Instances", f"inst{instance_num+1}.dat")
        instance_name = instance_num + 1
        output_file = os.path.join(".", "res", "MIP")
    
        m, n, L, S, D = read_mcp_instance(instance_file)

        for solver_name, solver in solvers.items():
            with mp.Manager() as manager:
                shared_list = manager.list()
                process = mp.Process(
                    target=solve_and_save,
                    args=(shared_list, m, n, L, S, D, solver)
                )
                process.start()
                process.join(timeout=300)
                if process.is_alive():
                    process.kill()
                    process.join()
                    process.close()
                if len(shared_list) == 0:
                    solution = {
                        'time': 300,
                        'optimal': False,
                        'obj': "N/A",
                        'sol': []
                    }
                else:
                    time, optimal, obj, sol = shared_list[-1]
                    solution = {
                        'time': time,
                        'optimal': optimal,
                        'obj': obj,
                        'sol': sol
                    }
                save_solution_to_json(instance_name, solver_name, solution, output_file)
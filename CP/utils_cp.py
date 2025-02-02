import re
import math
import os
import json


def extract_latest_decision(x_out):
    try:    
        #define regex patterns for the decision variables block
        vars_pattern = re.compile(
            r"(successor\s*=\s*\[.*?\];\s*"
            r"predecessor\s*=\s*\[.*?\];\s*"
            r"route_m\s*=\s*\[.*?\];\s*"
            r"load\s*=\s*\[.*?\];\s*"
            r"final_dist\s*=\s*\[.*?\];\s*"
            r"obj\s*=\s*\d+;)",
            re.DOTALL
        )

        vars_matches = vars_pattern.findall(x_out)




        latest_vars = vars_matches[-1].strip()


        init_time_pattern = re.compile(r"%%%mzn-stat:\s*initTime=([\d.]+)")
        solve_time_pattern = re.compile(r"%%%mzn-stat:\s*solveTime=([\d.]+)")


        init_time_matches = init_time_pattern.findall(x_out)
        solve_time_matches = solve_time_pattern.findall(x_out)


        latest_init_time = init_time_matches[-1]
        latest_solve_time = solve_time_matches[-1]

        #determine optimality based on the presence of '=========='
        optimal = "true" if "==========" in x_out else "false"

        #format the desired output
        desired_output = (
            f"{latest_vars}\n"
            f"----------\n"
            f"%%%mzn-stat: initTime={latest_init_time}\n"
            f"%%%mzn-stat: solveTime={latest_solve_time}\n"
            f"optimal = {optimal}"
        )

        return desired_output
    except Exception as e:
        return x_out



def parse_solution(desired_output):
    try:
        successor = list(map(int, re.search(r"successor = \[(.*?)\];", desired_output).group(1).split(", ")))
        predecessor = list(map(int, re.search(r"predecessor = \[(.*?)\];", desired_output).group(1).split(", ")))
        route_m = list(map(int, re.search(r"route_m = \[(.*?)\];", desired_output).group(1).split(", ")))
    
        return successor, predecessor, route_m
    except Exception as e :
        return None,None,None

def process_route_ms(successor, predecessor, route_m):
    try:
        m = max(route_m)
        n = len(route_m) - 2 * m
        couriers = {}
        for i, courier in enumerate(route_m):
            if courier not in couriers:
                couriers[courier] = []
            couriers[courier].append(i + 1)

        sorted_paths = {}
        for courier, nodes in couriers.items():
            path = []
            visited = set()
            current_node = None
            for node in nodes:
                if predecessor[node - 1] not in nodes:
                    current_node = node
                    break
            while current_node is not None and current_node not in visited:
                path.append(current_node)
                visited.add(current_node)
                next_node = successor[current_node - 1]
                current_node = next_node if next_node in nodes else None
            sorted_paths[courier] = [n + 1 if node >= n + 1 else node for node in path]

        return sorted_paths
    except Exception as e :
        return None

def save_solution(desired_output, instance_number, model_name, solver_name):
    try:
        #parse the solution
        successor, predecessor, route_m = parse_solution(desired_output)
        sorted_paths = process_route_ms(successor, predecessor, route_m)
        
        if  sorted_paths != None:
            
            #remove the first and last items from each courier's path
            processed_sol = {}
            for courier, path in sorted_paths.items():
                if len(path) > 2:
                    processed_sol[courier] = path[1:-1]
                else:
                    #if path has 2 or fewer nodes, removing first and last results in empty list
                    processed_sol[courier] = []

            #prepare the solution in the required format
            sol_list = [processed_sol[courier] for courier in sorted(processed_sol.keys())]

            # Try to match initTime, solveTime, obj, and optimal
            init_time_match = re.search(r"%%%mzn-stat:\s*initTime=([\d.]+)", desired_output)
            solve_time_match = re.search(r"%%%mzn-stat:\s*solveTime=([\d.]+)", desired_output)
            obj_match = re.search(r"obj\s*=\s*(\d+);", desired_output)
            optimal_match = re.search(r'optimal\s*=\s*(\w+)', desired_output)

            # Default/fallback values
            init_time = 0.0
            solve_time = 0.0
            obj = "No object"
            is_optimal = False

            # If 'optimal' was found, parse it
            if optimal_match:
                is_optimal = (optimal_match.group(1).lower() == 'true')

            # If we have numeric matches for init/solve times, parse them
            if init_time_match:
                init_time = float(init_time_match.group(1))
            if solve_time_match:
                solve_time = float(solve_time_match.group(1))

            # If we found an objective, parse it
            if obj_match:
                obj = int(obj_match.group(1))

            # Compute total time in ms
            total_time_ms = init_time + solve_time

            # If it is optimal, convert total time to seconds (floor); otherwise fallback to 300
            if is_optimal:
                time_sec = math.floor(total_time_ms)
            else:
                time_sec = 300

            # new_result then uses time_sec, is_optimal, obj, sol_list, etc.
            new_result = {
                f"{model_name}_{solver_name}": {
                    "time": time_sec,
                    "optimal": is_optimal,
                    "obj": obj,
                    "sol": sol_list
                }
            }
        else:
                    
                    new_result = {
            f"{model_name}_{solver_name}": {
                "time": 300,
                "optimal": False ,
                "obj": "N/A",
                "sol": []
            }
        }
    except Exception as e:
        new_result = {
            f"{model_name}_{solver_name}": {
                "time": 300,
                "optimal": False ,
                "obj": "N/A",
                "sol": []
            }
        }

   #get the parent directory of the script's location
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    #define output directory and JSON file path in the parent directory
    output_dir = os.path.join(parent_dir, "res", "CP")
    os.makedirs(output_dir, exist_ok=True)

    json_file = os.path.join(output_dir, f"{instance_number}.json")

    #Load existing data if JSON file exists
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                #If the file is empty or invalid, start with empty dict
                data = {}
    else:
        data = {}

    #Update data with new_result
    data.update(new_result)

    #save the updated data back to JSON file
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)


    return new_result

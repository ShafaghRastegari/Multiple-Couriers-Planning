import subprocess
import argparse
import shlex
import json
import os
import math
import re

def parse_solution(output):
    import re
    successor = list(map(int, re.search(r"successor = \[(.*?)\];", output).group(1).split(", ")))
    predecessor = list(map(int, re.search(r"predecessor = \[(.*?)\];", output).group(1).split(", ")))
    courier_route = list(map(int, re.search(r"courier_route = \[(.*?)\];", output).group(1).split(", ")))
    return successor, predecessor, courier_route

def process_courier_routes(successor, predecessor, courier_route):
    m = max(courier_route)
    n = len(courier_route) - 2 * m
    couriers = {}
    for i, courier in enumerate(courier_route):
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

def save_solution(output, time_taken, optimal, obj, instance_number, model_name, solver_name):
    # Post-process the solution
    successor, predecessor, courier_route = parse_solution(output)
    sorted_paths = process_courier_routes(successor, predecessor, courier_route)

    # Remove the first and last items from each courier's path
    processed_sol = {courier: path[1:-1] for courier, path in sorted_paths.items()}

    # Prepare the solution in the required format
    sol_list = [processed_sol[courier] for courier in sorted(processed_sol.keys())]

    # Create the result dictionary
    new_result = {
        solver_name: {
            "time": math.floor(time_taken) if optimal else 300,
            "optimal": optimal,
            "obj": obj,
            "sol": sol_list
        }
    }

    # Create the directory and prepare the JSON file
    output_dir = "res/CP"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{instance_number}.json")

    # Check if the file already exists and update it
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_results = json.load(f)
    else:
        existing_results = {}

    # Add the new result under the solver name
    existing_results.update(new_result)

    # Save the updated JSON
    with open(output_file, "w") as f:
        json.dump(existing_results, f, indent=4)

    print(f"Solution saved to {output_file}")

def run_minizinc(model_name, instance_number, solver_name, time_limit=300):
    if instance_number == 0:
        # Solve all instances from inst01.dzn to inst21.dzn
        for i in range(1, 11):
            run_minizinc(model_name, i, solver_name, time_limit)
        return

    # Generate file names
    model_file = f"{model_name}.mzn"
    data_file = f"inst{instance_number:02d}.dzn"
    time_limit_ms = time_limit * 1000
    command = f"minizinc --solver {solver_name} --time-limit {time_limit_ms} {model_file} {data_file}"

    try:
        result = subprocess.run(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=time_limit
        )

        if result.returncode == 0:
            print(f"Solution for instance {data_file} with model {model_file} using solver {solver_name}:")
            print(result.stdout)

            # Extract obj and runtime from the MiniZinc output
            obj_match = re.search(r"obj = (\d+);", result.stdout)
            obj = int(obj_match.group(1)) if obj_match else -1

            # Check if the result is optimal
            optimal = "==========" in result.stdout

            # Save the solution
            runtime = math.floor(time_limit if not optimal else result.stdout.count("=========="))
            save_solution(result.stdout, runtime, optimal, obj, instance_number, model_name, solver_name)

        else:
            print(f"Failed to find solution for instance {data_file} with model {model_file}.")
            print("Error message:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print(f"Execution timed out after {time_limit} seconds for instance {data_file}.")
        save_solution("", 300, False, -1, instance_number, model_name, solver_name)  # Save a placeholder if timeout

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MiniZinc with a specified model, solver, and instance.")
    parser.add_argument("method", type=str, help="Method (e.g., CP).")
    parser.add_argument("solver", type=str, help="Solver to use (e.g., gecode).")
    parser.add_argument("model", type=str, help="Name of the model file (without .mzn).")
    parser.add_argument("instance", type=int, help="Instance number to run (0 for all instances).")
    args = parser.parse_args()
    run_minizinc(args.model, args.instance, args.solver)

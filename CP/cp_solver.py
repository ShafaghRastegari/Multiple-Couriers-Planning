import subprocess
import shlex
import argparse
from .utils_cp import *


def run_minizinc(model_name, instance_number, solver_name, time_limit=300):
    if instance_number == 0:
        #Solve all instances from inst01.dzn to inst10.dzn
        for i in range(1, 11):
            run_minizinc(model_name, i, solver_name, time_limit)
        return

    #generate file names
    model_file = os.path.join("CP", f"{model_name}.mzn")
    data_file = os.path.join("CP", "data", f"inst{instance_number:02d}.dzn")
    time_limit_ms = time_limit * 1000
    command = f"minizinc --solver {solver_name} --time-limit {time_limit_ms} {model_file} {data_file} -s -a"

    all_output = []  # Variable to store all lines of output

    try:
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"Running MiniZinc with command: {command}")

        #read stdout line-by-line and save to the variable
        for line in iter(process.stdout.readline, ''):
            all_output.append(line.strip())  # Save to the list

        # Wait for the process to complete and capture any remaining output
        stdout, stderr = process.communicate()
        all_output.extend(stdout.splitlines())
        if stderr:
            all_output.append("\nError:\n" + stderr)

        #check the process return code
        if process.returncode == 0 or "==========" in stdout:
            print(f"Process completed for {data_file} with model {model_file} using solver {solver_name}.")
        else:
            print(f"Failed to find solution for instance {data_file} with model {model_file}.")
            print(f"Error message:\n{stderr}")

    except subprocess.TimeoutExpired:
        print(f"Execution timed out after {time_limit} seconds for instance {data_file}.")
        process.kill()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Join the output into a single string for easier display
    full_output = "\n".join(all_output)

    
    desired_output = extract_latest_decision(full_output)
    print(desired_output)
    print(save_solution(desired_output, instance_number, model_name, solver_name))

    return 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MiniZinc with a specified model, solver, and instance.")
    parser.add_argument("method", type=str, help="Method (e.g., CP).")
    parser.add_argument("solver", type=str, help="Solver to use (e.g., gecode).")
    parser.add_argument("model", type=str, help="Name of the model file (without .mzn).")
    parser.add_argument("instance", type=int, help="Instance number to run (0 for all instances).")
    args = parser.parse_args()
    run_minizinc(args.model, args.instance, args.solver)

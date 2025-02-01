import subprocess
import shlex
from .utils_cp import *
from .dat_to_dzn import *
import time


def run_minizinc(model_name, instance_number, solver_name, time_limit=300):
    if instance_number == 0:
        #Solve all instances from inst01 to inst21
        for i in range(1, 22):
            run_minizinc(model_name, i, solver_name, time_limit)
        return
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    in_file_path = os.path.join(project_root, 'Instances')
    out_file_path = os.path.join(os.path.dirname(__file__), 'data')
    start_time = time.perf_counter()
    data_to_dzn(in_file_path, out_file_path, instance_number)
    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000
    

    model_file = os.path.join("CP", f"{model_name}.mzn")
    data_file = os.path.join("CP", "data", f"inst{instance_number:02d}.dzn")
    time_limit_ms = (time_limit * 1000) - execution_time_ms
    command = f"minizinc --solver {solver_name} --time-limit {time_limit_ms} {model_file} {data_file} -s -a"

    all_output = []  

    try:
        process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"Running MiniZinc with command: {command}")

        
        for line in iter(process.stdout.readline, ''):
            all_output.append(line.strip())  

        #wait for the process to complete and take any remaining output
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

    
    full_output = "\n".join(all_output)

    #print(all_output)
    desired_output = extract_latest_decision(full_output)
    print(desired_output)
    print(save_solution(desired_output, instance_number, model_name, solver_name))

    return 


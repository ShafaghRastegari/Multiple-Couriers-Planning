import argparse
import importlib
import sys
import os
from SMT.SMT_handler import SMT_handler
from SAT.SAT_handler import SAT_function
from MIP.MIP import run_model

def main():
    commands = [
    "python solver.py -a CP -s gecode -m CP_sym -n 0",
    "python solver.py -a CP -s gecode -m CP_no_sym -n 0",
    "python solver.py -a CP -s gecode -m CPF_sym -n 0",
    "python solver.py -a CP -s gecode -m CPF_no_sym -n 0",
    "python solver.py -a CP -s chuffed -m CP_sym -n 0",
    "python solver.py -a CP -s chuffed -m CP_no_sym -n 0",
    "python solver.py -a CP -s chuffed -m CPF_sym -n 0",
    "python solver.py -a CP -s chuffed -m CPF_no_sym -n 0",
    ]
    # Add the project directory to sys.path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_dir)

    parser = argparse.ArgumentParser(description="Run a solver for a specified model and instance.")

    parser.add_argument("-a", "--approach", type=str, help="Solver method (e.g., CP, SAT, SMT, MIP).")

    parser.add_argument("-s", "--solver", type=str, help="Solver to use (e.g., gecode for CP).")

    parser.add_argument("-m", "--model", type=str, help="Name of the model file (without extension).")

    parser.add_argument("-n", "--num_instance", type=int, help="Instance number to run (0 for all instances).",
                        default=0)
    
    args = parser.parse_args()

    # Debug: Print the current working directory
    #print(f"Current working directory: {os.getcwd()}")

 

    if args.approach.lower() == "cp":
       # Debug: Print the import path
        module_path = f"{args.approach}.{args.approach.lower()}_solver"
        print(f"Attempting to import module: {module_path}")
        # Dynamically import the appropriate solver module based on the method
        try:
            solver_module = importlib.import_module(module_path)

            # Call the solver's run function
            if hasattr(solver_module, "run_minizinc"):
                solver_module.run_minizinc(args.model, args.num_instance, args.solver)
            else:
                print(f"Error: Solver module for method '{args.approach}' does not have a 'run_minizinc' function.")

        except ImportError as e:
            print(f"Error: Solver module for approach '{args.approach}' not found.")
            print(f"Details: {e}")
            return
        
    elif args.approach.lower() == "sat":
        SAT_function(num_instance=args.num_instance)

    elif args.approach.lower() == "smt":
        SMT_handler(num_instance=args.num_instance)

    elif args.approach.lower() == "mip":
        run_model(num_instance=args.num_instance)
    
    elif args.approach.lower() == "all":
        print("================CP Model=================")
        for cmd in commands:
            os.system(cmd)
            
        print("================SAT Model=================")
        SAT_function(num_instance=args.num_instance)
        
        print("================SMT Model=================")
        SMT_handler(num_instance=args.num_instance)
        
        print("================MIP Model=================")
        run_model(num_instance=args.num_instance)
        
    else:
        raise argparse.ArgumentError(None, "Please select a solver between CP, SAT, SMT and MIP")





if __name__ == "__main__":
    main()

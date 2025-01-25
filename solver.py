import argparse
import importlib
import sys
import os
from SMT.SMT_handler import SMT_handler

def main():
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
    print(f"Current working directory: {os.getcwd()}")

 

    if args.approach.lower() == "cp":
       # Debug: Print the import path
        module_path = f"{args.approach}.{args.approach.lower()}_solver"
        print(f"Attempting to import module: {module_path}")
        # Dynamically import the appropriate solver module based on the method
        try:
            solver_module = importlib.import_module(module_path)

            # Call the solver's run function
            if hasattr(solver_module, "run_minizinc"):
                solver_module.run_minizinc(args.model, args.instance, args.solver)
            else:
                print(f"Error: Solver module for method '{args.approach}' does not have a 'run_minizinc' function.")

        except ImportError as e:
            print(f"Error: Solver module for approach '{args.approach}' not found.")
            print(f"Details: {e}")
            return
        
    elif args.approach.lower() == "sat":
        pass

    elif args.approach.lower() == "smt":
        SMT_handler(num_instance=args.num_instance)#, model=args.model)

    elif args.approach.lower() == "mip":
        pass

    else:
        raise argparse.ArgumentError(None, "Please select a solver between CP, SAT, SMT and MIP")





if __name__ == "__main__":
    main()

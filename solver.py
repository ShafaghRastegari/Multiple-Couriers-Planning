import argparse
import importlib
import sys
import os

def main():
    # Add the project directory to sys.path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_dir)

    parser = argparse.ArgumentParser(description="Run a solver for a specified model and instance.")
    parser.add_argument("method", type=str, help="Solver method (e.g., CP, SAT, MIP).")
    parser.add_argument("solver", type=str, help="Solver to use (e.g., gecode for CP).")
    parser.add_argument("model", type=str, help="Name of the model file (without extension).")
    parser.add_argument("instance", type=int, help="Instance number to run (0 for all instances).")
    
    
    args = parser.parse_args()

    # Debug: Print the current working directory
    print(f"Current working directory: {os.getcwd()}")

    # Debug: Print the import path
    module_path = f"{args.method}.{args.method.lower()}_solver"
    print(f"Attempting to import module: {module_path}")

    # Dynamically import the appropriate solver module based on the method
    try:
        solver_module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"Error: Solver module for method '{args.method}' not found.")
        print(f"Details: {e}")
        return

    # Call the solver's run function
    if hasattr(solver_module, "run_minizinc"):
        solver_module.run_minizinc(args.model, args.instance, args.solver)
    else:
        print(f"Error: Solver module for method '{args.method}' does not have a 'run_minizinc' function.")

if __name__ == "__main__":
    main()
import gurobipy as gp

try:
    model = gp.Model()
    print("Gurobi license validated successfully!")
except gp.GurobiError as e:
    print(f"Gurobi Error: {e}")

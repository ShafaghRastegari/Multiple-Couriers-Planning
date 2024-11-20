from z3 import *
import numpy as np
from time import time
import json

models = [ "SMT_NO_SYM",
           "SMT_SYM",
          ]

def maximum(x):
    m = x[0]
    for v in x[1:]:
        m = If(v > m, v, m)
    return m

def run_model_on_instance(file):
    with open(file) as f:
      m = int(next(f)) # couriers
      n = int(next(f)) # items
      l = [int(e) for e in next(f).split()] # capacities
      s = [int(e) for e in next(f).split()] # max size of packages a courier can carry
      D = np.genfromtxt(f, dtype=int).tolist() # Distances
    return m, n, l, s, D

def add_sb_constraints(m, n, l, s, D, solver, X):
  # Add capacity-based symmetry-breaking constraints
  couriers_by_capacity = {}
  for idx, capacity in enumerate(l):
      if capacity not in couriers_by_capacity:
          couriers_by_capacity[capacity] = []
      couriers_by_capacity[capacity].append(idx)

  # Enforce symmetry-breaking constraints for couriers with identical capacities
  for capacity, courier_indices in couriers_by_capacity.items():
      for i in range(len(courier_indices) - 1):
          courier_1, courier_2 = courier_indices[i], courier_indices[i + 1]
          for item in range(n):
              # If courier_1 is assigned an item, then courier_2 cannot be assigned to the same item
              q = If(X[courier_1][item] > 0, True, False)
              p = If(X[courier_2][item] > 0, True, False)
              solver.add(Implies(q, Not(p)))

  # Symmetry-breaking constraints using cumulative load ordering
  for capacity, courier_indices in couriers_by_capacity.items():
    if len(courier_indices) > 1:
      for i in range(len(courier_indices) - 1):
        courier_1, courier_2 = courier_indices[i], courier_indices[i + 1]
        temp_1 = []
        temp_2 = []
        for j in range(n):
          temp_1.append(If(X[courier_1][j] > 0, True, False))
          temp_2.append(If(X[courier_2][j] > 0, True, False))
        load_1 = Sum([If(temp_1[j], s[j], 0) for j in range(n)])
        load_2 = Sum([If(temp_2[j], s[j], 0) for j in range(n)])
        solver.add(load_1 <= load_2)  # Enforce increasing load order

def SMT(m, n, l, s, D, sym_breaking=False):

  timeout = 300 # in seconds
  start_time = time()

  COURIERS = range(m)
  ITEMS = range(n)

  ####################################### DECISION VARIABLES #######################################

  # main decision variable: x[i,j] = k mean that the i-th courier is in j at time k
  X = [[Int(f'X_{i}_{j}') for j in ITEMS]for i in COURIERS]

  # variable for distance calculation
  dist = [Int(f'dist_{i}') for i in COURIERS]

  # variable for loads calculation
  load = [Int(f'load_{i}') for i in COURIERS]

  # the number of items that are delivered by each courier
  count = [Int(f'count_{i}') for i in COURIERS]

  solver = Solver()

  ####################################### CONSTRAINTS #######################################

  # Assignment Constraint
  for j in ITEMS:
    solver.add(Sum([If(X[i][j] > 0, 1, 0) for i in COURIERS]) == 1)

  for i in COURIERS:
    solver.add(Sum([If(X[i][j] > 0, 1, 0) for j in ITEMS]) >= 1)

  # Load Constraint
  for i in COURIERS:
    solver.add(Sum([If(X[i][j] > 0, s[j], 0) for j in ITEMS]) <= l[i])

  for i in COURIERS:  # For each courier
    # Calculate the number of assigned items (c) for courier i
    c = Sum([If(X[i][j] > 0, 1, 0) for j in ITEMS])
    solver.add(count[i] == c)
    # Distance from origin to the first item in the route
    dist_start = Sum([If(X[i][j] == 1, D[n][j], 0) for j in ITEMS])

    # Distance between consecutive items in the route
    dist_consecutive = Sum([
        If(And(X[i][j1] > 0, X[i][j2] > 0, X[i][j2] - X[i][j1] == 1), D[j1][j2], 0)
        for j1 in ITEMS for j2 in ITEMS
    ])

    # Distance from the last item in the route back to the origin
    dist_end = Sum([If(X[i][j] == c, D[j][n], 0) for j in ITEMS])

    # Total distance expression for courier i
    dist_expr = dist_start + dist_consecutive + dist_end

    # Add the constraint for the total distance of courier i
    solver.add(dist[i] == dist_expr)

  for i in COURIERS:
    for j in ITEMS:
      solver.add(And(X[i][j] >= 0, X[i][j] <= count[i]))

  for i in COURIERS:
    items = [If(X[i][j] > 0, X[i][j], -j) for j in ITEMS]
    solver.add(Distinct(items))

  if sym_breaking:
    add_sb_constraints(m, n, l, s, D, solver, X)

  ####################################### OBJECTIVE FUNCTION ######################################

  obj = Int('obj')
  solver.add(obj == maximum([dist[i] for i in COURIERS]))

  ######################################## SEARCH STRATEGY ########################################

  lower_bound_distance = max([D[n][j] + D[j][n] for j in ITEMS])
  solver.add(obj >= lower_bound_distance)

  ############################################# SOLVE #############################################
  solver.set("timeout", 300000)
  time_generation = time() - start_time

  if solver.check() != sat:
    print ("failed to solve")
    return None, None, None

  final_value = 0
  result_X_final = []
  while (solver.check() == sat) and (300 >= (time() - start_time)):

    model = solver.model()
    result_X = [ [ model.evaluate(X[i][j]) for j in ITEMS ]
            for i in COURIERS ]
    result_dist = [model.evaluate(dist[i]) for i in COURIERS]
    result_objective = model.evaluate(obj)

    result_X_final = result_X

    final_value = result_objective
    solver.add(obj < result_objective)

  final_time = (time() - time_generation - start_time)

  courier_path = []
  for i in COURIERS:
    temp = []
    for j in ITEMS:
      if result_X_final[i][j].as_long() > 0:
        temp.append(j + 1)
    courier_path.append(temp)
  return courier_path, final_value, final_time

for instance_num in range(10):
  final_result_dict = {}
  print(f"instance : {instance_num + 1}")
  for model in models:
    sym = None
    final_result_dict[model] = {}
    if model == "SMT_NO_SYM":
      sym = False
    else:
      sym = True
    #print(f"sym breaking: {sym}")
    courier_path, final_value, final_time = SMT(*run_model_on_instance(f"../Instances/inst0{instance_num+1}.dat" if instance_num < 9 else f"../Instances/inst{instance_num+1}.dat"),
                                                sym_breaking=sym)
    if courier_path is None:
      #print("No solution found")
      final_result_dict[model]["time"] = 300
      final_result_dict[model]["optimal"] = False
      final_result_dict[model]["obj"] = None
      final_result_dict[model]["sol"] = None
    else:
      if final_time is None:
        final_time = 300
      final_result_dict[model]["time"] = int(final_time)
      final_result_dict[model]["optimal"] = True if 300 > final_time else False
      final_result_dict[model]["obj"] = final_value.as_long()
      final_result_dict[model]["sol"] = courier_path

      #for i in range(len(courier_path)):
      #  print_matrix(courier_path[i])
      #print()
      #print(f"\n\nFinal objective: {final_value}")
      #print(f"Finished in: {final_time:.3} seconds\n")
    print("finished")
  with open(f'../res/SMT/{instance_num+1}.json', 'w') as f:
    json.dump(final_result_dict, f, indent=1)
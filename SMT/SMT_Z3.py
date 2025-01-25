from z3 import *
import numpy as np
from time import time
from SMT.utils import *
from utils import *

def SMT(shared_list, m, n, l, s, D, sym_breaking=False):

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
    load[i] = Sum([If(X[i][j] > 0, s[j], 0) for j in ITEMS])
    solver.add(load[i] <= l[i])

  for i in COURIERS:  # For each courier
    # Calculate the number of assigned items (c) for courier i

    count[i] = Sum([If(X[i][j] > 0, 1, 0) for j in ITEMS])

    #solver.add(count[i] == c)
    # Distance from origin to the first item in the route
    dist_start = Sum([If(X[i][j] == 1, D[n][j], 0) for j in ITEMS])

    # Distance between consecutive items in the route
    dist_consecutive = Sum([
        If(And(X[i][j1] > 0, X[i][j2] > 0, X[i][j2] - X[i][j1] == 1), D[j1][j2], 0)
        for j1 in ITEMS for j2 in ITEMS
    ])

    # Distance from the last item in the route back to the origin
    dist_end = Sum([If(X[i][j] == count[i], D[j][n], 0) for j in ITEMS])

    # Total distance expression for courier i
    dist_expr = dist_start + dist_consecutive + dist_end

    # Add the constraint for the total distance of courier i
    dist[i] = dist_expr

  for i in COURIERS:
    for j in ITEMS:
      solver.add(And(X[i][j] >= 0, X[i][j] <= count[i]))

  # Each items that is delivered in different time(k) by i th couriesr
  for i in COURIERS:
    items = [If(X[i][j] > 0, X[i][j], -j) for j in ITEMS]
    solver.add(Distinct(items))

  if sym_breaking:
    add_sb_constraints(m, n, l, s, D, solver, X)

  ####################################### OBJECTIVE FUNCTION ######################################

  obj = Int('obj')
  obj = maximum([dist[i] for i in COURIERS])

  ######################################## LOWER AND UPPER BOUNDS ########################################

  max_distances = [max(D[i][:-1]) for i in ITEMS]
  # print(f"before sort : {max_distances}")
  max_distances.sort()
  # print(f"after sort : {max_distances}")
  
  #upper_bound = sum(max_distances[m:]) + max(D[n]) + max([D[j][n] for j in ITEMS])
  upper_bound = calculate_upper_bound(m, n, l, s, D)
  
  # lower_bound_distance = max([D[n][j] + D[j][n] for j in ITEMS])
  lower_bound_distance = calculate_lower_bound(n, D)
  print(f"lower bound distance : {lower_bound_distance}")
  print(f"upper bound distance : {upper_bound}")

  solver.add(obj >= lower_bound_distance)
  solver.add(obj <= upper_bound)

  #print(lower_bound_distance)

  ############################################# SOLVE #############################################
  solver.set("timeout", 300000)
  time_generation = time() - start_time
  print(f"generation time :{time_generation}")
  final_value = 0
  result_X_final = []
  result_count_final = []
  final_time = 0
  optimal = True

  if solver.check() != sat:
    print ("failed to solve")
    shared_list.append((None, None, None, False))
    #return None, None, None, False
  while (solver.check() == sat):
    print(f"solving time :{time() - start_time}")
    model = solver.model()
    result_X = [ [ model.evaluate(X[i][j]) for j in ITEMS ]
            for i in COURIERS ]
    result_dist = [model.evaluate(dist[i]) for i in COURIERS]
    result_count = [model.evaluate(count[i]) for i in COURIERS]
    result_objective = model.evaluate(obj)

    result_X_final = result_X

    final_value = result_objective
    solver.add(obj < result_objective)

    result_count_final = result_count
    final_time = (time() - time_generation - start_time)

    courier_path = courier_path_from_result(result_count_final, result_X_final
                                            , COURIERS, ITEMS)
    shared_list.append((courier_path, final_value.as_long(), final_time, optimal))

    print(f"shared_list length : {len(shared_list)}")
    #return courier_path, final_value, final_time, optimal

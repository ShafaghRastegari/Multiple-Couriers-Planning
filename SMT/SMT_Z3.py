from z3 import *
import numpy as np
from time import time
from SMT.utils import *
from SMT.additional_constraints import *
from utils import *

def SMT(shared_list, m, n, l, s, D, sym_breaking=False, imp_cons=True):

  start_time = time()

  COURIERS = range(m)
  ITEMS = range(n)

  ####################################### DECISION VARIABLES #######################################
  # main decision variable: x[i,j] = k mean that the i-th courier collect the j-th item at time k
  X = [[Int(f'X_{i}_{j}') for j in ITEMS]for i in COURIERS]

  # stores the total distance traveled by each courier.
  dist = [Int(f'dist_{i}') for i in COURIERS]

  # stores the total load of items collected by each courier
  load = [Int(f'load_{i}') for i in COURIERS]

  # the number of items that are collected by each courier
  count = [Int(f'count_{i}') for i in COURIERS]

  solver = Solver()
  ####################################### CONSTRAINTS #######################################

  # Each item is collected by exactly one courier
  for j in ITEMS:
    solver.add(Sum([If(X[i][j] > 0, 1, 0) for i in COURIERS]) == 1)

  # The total weight of items collected by each courier must not exceed the courier's load capacity
  for i in COURIERS:
    load[i] = Sum([If(X[i][j] > 0, s[j], 0) for j in ITEMS])
    solver.add(load[i] <= l[i])

  for i in COURIERS:  # For each courier
    # Calculate the number of assigned items (c) for courier i

    count[i] = Sum([If(X[i][j] > 0, 1, 0) for j in ITEMS])
    
    
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

  # X array boundries in k value
  for i in COURIERS:
    for j in ITEMS:
      solver.add(And(X[i][j] >= 0, X[i][j] <= count[i]))

  # Each item is delivered at a different time(k) by i-th couriesr
  for i in COURIERS:
    items = [If(X[i][j] > 0, X[i][j], -j) for j in ITEMS]
    solver.add(Distinct(items))

  if sym_breaking:
    add_sb_constraints(m, l, solver, X, load)
  if imp_cons:
    add_implied_constraints(m, n, solver, X, count)

  ####################################### OBJECTIVE FUNCTION ######################################

  obj = Int('obj')
  obj = maximum([dist[i] for i in COURIERS])

  ######################################## LOWER AND UPPER BOUNDS ########################################

  upper_bound = calculate_upper_bound(m, n, l, s, D)
  
  lower_bound_distance = calculate_lower_bound(n, D)

  solver.add(obj >= lower_bound_distance)
  solver.add(obj <= upper_bound)

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
    # index1, index2 = add_sb_constraints(m, n, l, solver, X)
    # print(f"result X index 1: {result_X[index1]}")
    # print(f"result X index 2: {result_X[index2]}")
    final_value = result_objective
    solver.add(obj < result_objective)

    result_count_final = result_count
    final_time = (time() - time_generation - start_time)

    courier_path = courier_path_from_result(result_count_final, result_X_final
                                            , COURIERS, ITEMS)
    # print(f"courier path : {courier_path}")
    print(f"obj : {final_value}")
    shared_list.append((courier_path, final_value.as_long(), final_time, optimal))

    # print(f"shared_list length : {len(shared_list)}")
    #return courier_path, final_value, final_time, optimal

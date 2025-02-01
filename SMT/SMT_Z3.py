from z3 import *
import numpy as np
from time import time
from SMT.utils import *
from SMT.constraints import *
from utils import *

def SMT_Solver(shared_list, m, n, l, s, D, sym_breaking=False, imp_cons=True):

  start_time = time()

  COURIERS = range(m)
  ITEMS = range(n)

  ###################### DECISION VARIABLES ##################

  # main decision variable: x[i,j] = k mean that the i-th courier collect the j-th item at time k
  X = [[Int(f'X_{i}_{j}') for j in ITEMS]for i in COURIERS]

  # stores the total distance traveled by each courier.
  dist = [Int(f'dist_{i}') for i in COURIERS]

  # stores the total load of items collected by each courier
  load = [Int(f'load_{i}') for i in COURIERS]

  # the number of items that are collected by each courier
  count = [Int(f'count_{i}') for i in COURIERS]

  solver = Solver()

  ###################### CONSTRAINTS ######################

  add_constraints(solver, load, count, dist, X, m, n, l, s, D, sym_breaking, imp_cons)

  ###################### OBJECTIVE FUNCTION ################

  obj = Int('obj')
  obj = maximum([dist[i] for i in COURIERS])

  ###################### LOWER AND UPPER BOUNDS ############

  upper_bound = calculate_upper_bound(m, n, l, s, D)
  
  lower_bound_distance = calculate_lower_bound(n, D)

  solver.add(obj >= lower_bound_distance)
  solver.add(obj <= upper_bound)

  ###################### SOLVE ############################

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

  while (solver.check() == sat):
    print(f"solving time :{time() - start_time}")
    model = solver.model()
    result_X = [ [ model.evaluate(X[i][j]) for j in ITEMS ]
            for i in COURIERS ]
    
    # result_dist = [model.evaluate(dist[i]) for i in COURIERS]
    result_count = [model.evaluate(count[i]) for i in COURIERS]
    result_objective = model.evaluate(obj)

    result_X_final = result_X
    final_value = result_objective
    solver.add(obj < result_objective)

    result_count_final = result_count
    final_time = (time() - time_generation - start_time)

    courier_path = courier_path_from_result(result_count_final, result_X_final
                                            , COURIERS, ITEMS)
    
    print(f"obj : {final_value}")
    shared_list.append((courier_path, final_value.as_long(), final_time, optimal))

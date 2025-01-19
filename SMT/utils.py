from z3 import *
import numpy as np

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

def courier_path_from_result(result_count_final, result_X_final, COURIERS, ITEMS):
  courier_path = []
  for i in COURIERS:
      temp = [0] * result_count_final[i].as_long()
      temp_index = 0
      for j in ITEMS:
        if result_X_final[i][j].as_long() > 0:
          temp[result_X_final[i][j].as_long() - 1] = j + 1
          temp_index += 1
      courier_path.append(temp)
  return courier_path
  
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




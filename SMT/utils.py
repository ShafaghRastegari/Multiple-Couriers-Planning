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

def pars_model(model):

  if model == "SMT":
    sym = False
    imp = False
  elif model == "SMT_SYM":
    sym = True
    imp = False
  if model == "SMT_IMP":
    sym = False
    imp = True
  elif model[1] == "SMT_SYM_IMP":
    sym = True
    imp = True
    
  print(f"SYMMETRY BREAKING : {sym},  IMPLIED CONSTRAINT : {imp}")
  return sym, imp
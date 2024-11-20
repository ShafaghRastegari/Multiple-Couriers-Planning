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
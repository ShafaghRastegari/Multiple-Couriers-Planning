from z3 import *
import numpy as np

def add_sb_constraints(m, n, l, solver, X):

  load = {}
  for i in range(m):
    if l[i] not in load:
        load[l[i]] = [i]  # Initialize a new list for the key
    else:
        load[l[i]].append(i)  # Append to the existing list

  # print(f"load : {load}")
  sorted_load = sorted(load.items(),reverse=True)

  print(f"sorted_load : {sorted_load}")
  for d_l in sorted_load:
    if len(d_l[1]) > 1:
      print(d_l[1])
      for index_ in range(len(d_l[1]) - 1): 
        print(f"index : {d_l[1][index_]}")
        print(f"index : {d_l[1][index_ + 1]}")
        # return d_l[1][index_], d_l[1][index_ + 1]
        #  solver.add(count[index_])
        solver.add(X[d_l[1][index_]] < X[d_l[1][index_ + 1]])
        # solver.add(X[index_] > X[index_ + 1])

def add_implied_constraints(m, n, solver, X, count):

    print("###################################IMPLIED CONSTRAINT########################################")
    
    max_item = int(n / m) + 1

    # Each courier collects more than one item
    for i in range(m):
        solver.add(Sum([If(X[i][j] > 0, 1, 0) for j in range(n)]) >= 1)

        # balance item distribution
        
        solver.add(count[i] <= max_item)
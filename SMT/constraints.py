from z3 import *
import numpy as np


def add_constraints(solver, load, count, dist, X, m, n, l, s, D, sym_breaking, imp_cons):
  COURIERS = range(m)
  ITEMS = range(n)
  
  # Each item is collected by exactly one courier
  for j in ITEMS:
    solver.add(Sum([If(X[i][j] > 0, 1, 0) for i in COURIERS]) == 1)

  # The total weight of items collected by each courier must not exceed the courier's load capacity
  for i in COURIERS:
    load[i] = Sum([If(X[i][j] > 0, s[j], 0) for j in ITEMS])
    solver.add(load[i] <= l[i])

  for i in COURIERS:  

    # Calculate the number of items assigned to each courier (c)
    count[i] = Sum([If(X[i][j] > 0, 1, 0) for j in ITEMS])
    
    
    # Distance from origin to the first item that courier i collect
    dist_start = Sum([If(X[i][j] == 1, D[n][j], 0) for j in ITEMS])

    # Distance between consecutive items in the courier i's route
    dist_consecutive = Sum([
        If(And(X[i][j1] > 0, X[i][j2] > 0, X[i][j2] - X[i][j1] == 1), D[j1][j2], 0)
        for j1 in ITEMS for j2 in ITEMS
    ])

    # Distance from the last item in the courier i's route back to the origin
    dist_end = Sum([If(X[i][j] == count[i], D[j][n], 0) for j in ITEMS])

    # Total distance expression for courier i
    dist_expr = dist_start + dist_consecutive + dist_end

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


def add_sb_constraints(m, l, solver, X, load):
    
    for i in range(m - 1):
        for j in range(i + 1, m):
            if l[i] >= l[j] :
                # Ensure the first item of courier i is less than that of courier j
                solver.add(load[i] > load[j])
                break # I don't want to say A < B, A < D,  A < F, B < D, B < F, D < F. Instead I want to say A < B, B < D, D < F
               
               
def add_implied_constraints(m, n, solver, X, count):

    max_item = int(n / m) + 1

    # Each courier collects more than one item
    for i in range(m):
        solver.add(Sum([If(X[i][j] > 0, 1, 0) for j in range(n)]) >= 1)

        # balance item distribution
        solver.add(count[i] <= max_item)
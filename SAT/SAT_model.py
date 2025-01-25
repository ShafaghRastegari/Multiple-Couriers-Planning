import math
from SAT_project.Instance import *
#from SAT.src.SAT_utils import *
#from constants import *
from z3.z3 import *
from SAT_project.utils_SAT import *
import time as T

def sat_solver1(instance, solver, timeout, pre_time, strategy="", sym_breaking=False):
    solver.set('timeout', timeout * 1000)
    variables = constraints(instance, solver, sym_breaking)
    a, t, distance, w, encode_time = variables
    if encode_time == 300:
        return 300, False, "N/A", []
    timeout = int((timeout - encode_time))
    solver.set('timeout', timeout * 1000)
    time_search, optimal, obj, sol = search_optimize(instance, strategy, variables, solver, timeout)
    time = time_search + encode_time + pre_time
    print(f"time search:{time_search}, encode time:{encode_time}, pre_time: {pre_time}")
    print("Time from beginning of the computation:", np.round(time, 2), "seconds")
    return time, optimal, obj, sol

def search_optimize(instance, strategy, variables, solver, timeout):
    if strategy == "linear":
        time, optimal, obj, sol = linear_search(solver, instance, variables, timeout)
    elif strategy == "binary":
        time, optimal, obj, sol = binary_search(solver, instance, variables, timeout)

    return time, optimal, obj, sol

def display(orders, distances_bin, obj_value, assignments):

    distances = [binary_to_int(d) for d in distances_bin]

    print(f"-----------Objective value: {obj_value}-----------")
    print(f"------------------Routes-----------------")
    m = len(assignments)
    n = len(assignments[0])
    routes = [[0 for j in range(n)] for i in range(m)]
    for node in range(n):
        for time in range(n):
            if orders[node][time]:
                for courier in range(m):
                    if assignments[courier][node]:
                        routes[courier][time] = node+1
                        break
                break

    routes = [[x for x in row if x != 0] for row in routes]
    for courier in range(m):
        print("Origin --> " +
              ' --> '.join([str(node) for node in routes[courier]]) +
              f' --> Origin: travelled {distances[courier]}')

    tot_s = []
    for courier in range(m):
        sol = []
        for item in routes[courier]:
            sol.append(item)

        tot_s.append(sol)

    return distances, tot_s


def linear_search(solver, instance, variables, timeout):
    start_time = T.time()
    a, t, distances, _, _ = variables
    m = instance.m
    n = instance.n
    max_Distance_Binary = num_bits(instance.upper_bound)
    lower_bound = instance.lower_bound
    upper_bound = instance.upper_bound
    last_model = None
    objective_value = None
    optimal = True
    solver.push()
    flag = True
    count = 0
    time_flag = 0
    while flag:
        status = solver.check()
        if status == sat:
            count += 1
            model = solver.model()
            last_model = model
            current_time = T.time()
            past_time = int((current_time - start_time))
            solver.set('timeout', (timeout - past_time) * 1000)
            objective_value = -1
            for i in range(len(distances)):
                dist = binary_to_int([1 if model.evaluate(distances[i][j]) else 0 for j in range(max_Distance_Binary)])
                objective_value = max(objective_value, dist)

            print(f"This model obtained objective value: {objective_value}")

            if objective_value <= lower_bound:
                break

            upper_bound = objective_value - 1
            upper_bound_bin = int_to_binary(upper_bound, num_bits(upper_bound), BoolVal)

            solver.pop()
            solver.push()

            solver.add(All_Less_bin(distances, upper_bound_bin))

        elif status == unsat:
            if count == 0:
                print("UNSAT")
                current_time = T.time()
                past_time = int((current_time - start_time))
                return past_time, False, "N/A", []
            flag = False
        elif status == unknown:
            if count == 0:
                print("UNKNOWN RESULT for insufficient time")
                return timeout, False, "N/A", []
            else:
                time_flag = timeout
            flag = False
            optimal = False

    model = last_model
    a = [[model.evaluate(a[i][j]) for j in range(n)] for i in range(m)]
    t = [[model.evaluate(t[j][k]) for k in range(n // m + 1)] for j in range(n)]
    dist = [[model.evaluate(distances[i][b]) for b in range(max_Distance_Binary)] for i in range(m)]
    distances, tot_s = display(t, dist, objective_value, a)
    distances, tot_s = instance.invert_sort_weight(distances, tot_s)
    current_time = T.time()
    past_time = current_time - start_time
    if time_flag == timeout:
        past_time = timeout

    return int(past_time), optimal, objective_value, tot_s

def binary_search(solver, instance, variables, timeout):
    start_time = T.time()
    a, t, distances, _, encode_time = variables
    m = instance.m
    n = instance.n
    D = instance.D
    max_Distance_Binary = num_bits(instance.upper_bound)

    upper_bound = instance.upper_bound
    lower_bound = instance.lower_bound

    optimal = True
    time_flag = 0
    last_model = None

    upper_bound_bin = int_to_binary(upper_bound, max_Distance_Binary, BoolVal)

    solver.add(All_Less_bin(distances, upper_bound_bin))

    lower_bound_bin = int_to_binary(lower_bound, max_Distance_Binary, BoolVal)
    solver.add(At_LeastOne_Greater_bin(distances, lower_bound_bin))
    solver.push()
    count = 0
    flag = True
    while lower_bound <= upper_bound and flag:
        if upper_bound - lower_bound <= 1:
            mid = (lower_bound + upper_bound) // 2
            mid_bin = int_to_binary(mid, num_bits(mid), BoolVal)
        else:
            mid = (lower_bound + upper_bound - 1) // 2
            mid_bin = int_to_binary(mid, num_bits(mid), BoolVal)

        solver.add(All_Less_bin(distances, mid_bin))

        print(f"Trying with bounds: [{lower_bound}, {upper_bound}] and posing obj_val <= {mid}")

        current_time = T.time()
        past_time = int(current_time - start_time)
        solver.set('timeout', (timeout - past_time) * 1000)
        status = solver.check()
        if status == sat:
            count += 1
            model = solver.model()
            last_model = model
            objective_value = -1
            for i in range(m):
                dist = binary_to_int([1 if model.evaluate(distances[i][j]) else 0 for j in range(max_Distance_Binary)])
                objective_value = max(objective_value, dist)

            print(f"This model obtained objective value: {objective_value} ")

            if objective_value <= 1:
                break

            upper_bound = objective_value - 1
            upper_bound_bin = int_to_binary(upper_bound, num_bits(upper_bound), BoolVal)

        elif status == unsat:
            if count == 0:
                print("UNSAT")
                past_time = int((current_time - start_time))
                return past_time, False, "N/A", []
            count += 1
            solver.pop()
            solver.push()
            lower_bound = mid + 1
            lower_bound_bin = int_to_binary(lower_bound, num_bits(lower_bound), BoolVal)
        elif status == unknown:
            if count == 0:
                print("UNKNOWN RESULT for insufficient time")
                return timeout, False, "N/A", []
            else:
                time_flag = timeout
            flag = False
            optimal = False

        solver.pop()
        solver.push()
        solver.add(All_Less_bin(distances, upper_bound_bin))
        solver.add(At_LeastOne_Greater_bin(distances, lower_bound_bin))


    model = last_model
    a = [[model.evaluate(a[i][j]) for j in range(n)] for i in range(m)]
    t = [[model.evaluate(t[j][k]) for k in range(n // m + 1)] for j in range(n)]
    dist = [[model.evaluate(distances[i][b]) for b in range(max_Distance_Binary)] for i in range(m)]
    distances, tot_s = display(t, dist, objective_value, a)
    distances, tot_s = instance.invert_sort_weight(distances, tot_s)
    current_time = T.time()
    past_time = current_time - start_time
    if time_flag == timeout:
        past_time = timeout

    return int(past_time), optimal, objective_value, tot_s


def constraints(instance, solver, sym_breaking):

    start_time = T.time()
    m = instance.m
    n = instance.n
    s = instance.s
    l = instance.l
    D = instance.D

    s_copy = s[:]
    s_copy.sort(reverse=True)
    sum_s_item = s_copy[0]
    count = 1
    while count < len(s):
        if sum_s_item + s_copy[count] <= max(l):
            sum_s_item += s_copy[count]
            count += 1
        else:
            break

    max_weight_Binary = num_bits(sum_s_item)
    max_Distance_Binary = num_bits(instance.upper_bound)

    a = [[Bool(f"a_{i}_{j}") for j in range(n)] for i in range(m)]
    x = [[[Bool(f"x_{i}_{j}_{k}") for k in range(n + 1)] for j in range(n + 1)] for i in range(m)]
    t = [[Bool(f"deliver_{j}_as_{k}-th") for k in range(n // m + 1)] for j in range(n)]
    w = [[Bool(f"cl_{i}_{k}") for k in range(max_weight_Binary)] for i in range(m)]
    l_bin = [[BoolVal(b) for b in int_to_binary(l[i], length=num_bits(l[i]))] for i in range(m)]
    s_bin = [[BoolVal(b) for b in int_to_binary(s[j], length=num_bits(s[j]))] for j in range(n)]
    flat_D = flatten_matrix(D)
    flat_D_bin = [int_to_binary(e, num_bits(e) if e > 0 else 1, BoolVal) for e in flat_D]
    distances = [[Bool(f"dist_bin_{i}_{k}") for k in range(max_Distance_Binary)] for i in range(m)]

    if sym_breaking:

        solver.add(sort_decreasing(w))
        for i in range(m - 1):
            solver.add(Implies(equals(w[i], w[i+1]), less(a[i], a[i+1])))
        '''for i in range(m - 1):
            if l[i] == l[i+1]:
                solver.add(less(a[i], a[i+1]))
            else: # l[i] > l[i+1]
                solver.add(less(w[i+1], w[i]))'''

    for j in range(n):
        solver.add(exactly_one([a[i][j] for i in range(m)], f"assignment_{j}"))

    for i in range(m):
        solver.add(conditional_sum(a[i], s_bin, w[i], f"compute_courier_load_{i}"))
        solver.add(less(w[i], l_bin[i]))

    for i in range(m):
        solver.add(at_least_one(a[i]))

    for i in range(n):
        solver.add(exactly_one(t[i], f"time_of_{i}"))

    for i in range(m):
        solver.add(And([Not(x[i][j][j]) for j in range(n + 1)]))

        for j in range(n):
            solver.add(Implies(a[i][j], exactly_one(x[i][j], f"courier_{i}_leaves_{j}")))
            solver.add(Implies(Not(a[i][j]), allfalse(x[i][j])))
        solver.add(exactly_one(x[i][n], f"courier_{i}_leaves_origin"))

        for k in range(n):
            solver.add(Implies(a[i][k], exactly_one([x[i][j][k] for j in range(n + 1)], f"courier_{i}_reaches_{k}")))
            solver.add(Implies(Not(a[i][k]), allfalse([x[i][j][k] for j in range(n + 1)])))
        solver.add(exactly_one([x[i][j][n] for j in range(n + 1)], f"courier_{i}_returns_to_origin"))

        for j in range(n):
            for k in range(n):
                solver.add(Implies(x[i][j][k], consecutive(t[j], t[k])))
            solver.add(Implies(x[i][n][j], t[j][0]))

    flat_x = [flatten_matrix(x[i]) for i in range(m)]

    for i in range(m):
        solver.add(conditional_sum(flat_x[i], flat_D_bin, distances[i], f"distances_def_{i}"))


    solver.push()
    encoding_time = T.time()
    encode_time = int(encoding_time - start_time)
    print(f"Encoding finished at time {encode_time}s, now start solving/optimization search")

    return a, t, distances, w, encode_time


import math
from SAT.Instance import *
from z3.z3 import *
from SAT.utils_SAT import *
import time as T

def sat_solver(shared_list, instance, timeout, pre_time, strategy="", sym_breaking=False, implied_constraint = False):
    solver = Solver()
    set_param("sat.random_seed", 42)
    solver.set('timeout', timeout * 1000)
    variables = constraints(instance, solver, sym_breaking, implied_constraint)
    a, t, distance, w, encode_time = variables
    timeout = int((timeout - encode_time))
    solver.set('timeout', timeout * 1000)
    time_search, optimal, obj, sol, travel = search_optimize(instance, strategy, variables, solver, timeout, shared_list, implied_constraint)
    time = time_search + encode_time + pre_time
    print(f"time search:{time_search}, encode time:{encode_time}, pre_time: {pre_time}")
    print("Time from beginning of the computation:", np.round(time, 2), "seconds")
    shared_list.append((time, optimal, obj, sol, travel))


def search_optimize(instance, strategy, variables, solver, timeout, shared_list, implied_constraint):
    if strategy == "linear":
        time, optimal, obj, sol, travel = linear_search(solver, instance, variables, timeout, shared_list, implied_constraint)
    elif strategy == "binary":
        time, optimal, obj, sol, travel = binary_search(solver, instance, variables, timeout, shared_list, implied_constraint)

    return time, optimal, obj, sol, travel

def display(orders, distances_bin, obj_value, assignments, show = True):

    distances = [binary_to_int(d) for d in distances_bin]
    if show:
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
    if show:
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

def linear_search(solver, instance, variables, timeout, shared_list, implied_constraint):
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
    upper_bound_bin = int_to_binary(upper_bound, num_bits(upper_bound), BoolVal)
    solver.add(All_Less_bin(distances, upper_bound_bin))
    lower_bound_bin = int_to_binary(lower_bound, num_bits(lower_bound), BoolVal)
    solver.add(At_LeastOne_Greater_bin(distances, lower_bound_bin))
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
            
            a_eval = [[model.evaluate(a[i][j]) for j in range(n)] for i in range(m)]
            if implied_constraint:
                t_eval = [[model.evaluate(t[j][k]) for k in range(n // m + 1)] for j in range(n)]
            else:
                t_eval = [[model.evaluate(t[j][k]) for k in range(n)] for j in range(n)]
                
            dist_eval = [[model.evaluate(distances[i][b]) for b in range(max_Distance_Binary)] for i in range(m)]
            distances_1, tot_s = display(t_eval, dist_eval, objective_value, a_eval, False)
            distances_1, tot_s = instance.invert_sort_weight(distances_1, tot_s)
            current_time = T.time()
            past_time = current_time - start_time
            shared_list.append((int(past_time), optimal, objective_value, tot_s, distances_1))

        elif status == unsat:
            if count == 0:
                print("UNSAT")
                current_time = T.time()
                past_time = int((current_time - start_time))
                return past_time, False, "N/A", [], []
            flag = False
        elif status == unknown:
            if count == 0:
                print("UNKNOWN RESULT for insufficient time")
                return timeout, False, "N/A", [], []
            else:
                time_flag = timeout
            flag = False
            optimal = False



    model = last_model
    a = [[model.evaluate(a[i][j]) for j in range(n)] for i in range(m)]
    if implied_constraint:
        t = [[model.evaluate(t[j][k]) for k in range(n // m + 1)] for j in range(n)]
    else:
        t = [[model.evaluate(t[j][k]) for k in range(n)] for j in range(n)]
    dist = [[model.evaluate(distances[i][b]) for b in range(max_Distance_Binary)] for i in range(m)]
    distances, tot_s = display(t, dist, objective_value, a, False)
    distances, tot_s = instance.invert_sort_weight(distances, tot_s)
    current_time = T.time()
    past_time = current_time - start_time
    if time_flag == timeout:
        past_time = timeout

    return int(past_time), optimal, objective_value, tot_s, distances

def binary_search(solver, instance, variables, timeout, shared_list, implied_constraints):
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

    lower_bound_bin = int_to_binary(lower_bound, num_bits(lower_bound), BoolVal)
    solver.add(At_LeastOne_Greater_bin(distances, lower_bound_bin))
    solver.push()
    count = 0
    flag = True
    binary_section = 1
    while lower_bound <= upper_bound and flag:
        if upper_bound - lower_bound <= 1:
            mid = (lower_bound + upper_bound) // 2
            mid_bin = int_to_binary(mid, num_bits(mid), BoolVal)
        else:
            mid = (lower_bound + upper_bound - 1) // 2
            mid_bin = int_to_binary(mid, num_bits(mid), BoolVal)

        solver.add(All_Less_bin(distances, mid_bin))

        print(f"Trying with bounds: [{lower_bound}, {upper_bound}] and try obj_val <= {mid}")

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
            
            a_eval = [[model.evaluate(a[i][j]) for j in range(n)] for i in range(m)]
            if implied_constraints:
                t_eval = [[model.evaluate(t[j][k]) for k in range(n // m + 1)] for j in range(n)]
            else:
                t_eval = [[model.evaluate(t[j][k]) for k in range(n)] for j in range(n)]
            dist_eval = [[model.evaluate(distances[i][b]) for b in range(max_Distance_Binary)] for i in range(m)]
            distances_1, tot_s = display(t_eval, dist_eval, objective_value, a_eval, False)
            distances_1, tot_s = instance.invert_sort_weight(distances_1, tot_s)
            current_time = T.time()
            past_time = current_time - start_time
            shared_list.append((int(past_time), False, objective_value, tot_s, distances_1))

        elif status == unsat:
            if count == 0:
                binary_section = 2
                
            if count == 1 and binary_section == 2:
                print("UNSAT")
                past_time = int((current_time - start_time))
                return past_time, False, "N/A", [], []
            count += 1
            solver.pop()
            solver.push()
            lower_bound = mid + 1
            lower_bound_bin = int_to_binary(lower_bound, num_bits(lower_bound), BoolVal)
        elif status == unknown:
            if count == 0:
                print("UNKNOWN RESULT for insufficient time")
                return timeout, False, "N/A", [], []
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
    if implied_constraints:
        t = [[model.evaluate(t[j][k]) for k in range(n//m + 1)] for j in range(n)]
    else:
        t = [[model.evaluate(t[j][k]) for k in range(n)] for j in range(n)]
    dist = [[model.evaluate(distances[i][b]) for b in range(max_Distance_Binary)] for i in range(m)]
    distances, tot_s = display(t, dist, objective_value, a, False)
    distances, tot_s = instance.invert_sort_weight(distances, tot_s)
    current_time = T.time()
    past_time = current_time - start_time
    if time_flag == timeout:
        past_time = timeout

    return int(past_time), optimal, objective_value, tot_s, distances


def constraints(instance, solver, sym_breaking, implied_constraint):

    start_time = T.time()
    m = instance.m
    n = instance.n
    s = instance.s
    l = instance.l
    D = instance.D

    max_weight_Binary = num_bits(max(l))
    max_Distance_Binary = num_bits(instance.upper_bound)

    # a_ij = True indicates that courier i delivers object j
    a = [[Bool(f"a_{i}_{j}") for j in range(n)] for i in range(m)]
    # x_ijk = 1 indicates that courier i moves from delivery point j to delivery point k in his route
    x = [[[Bool(f"x_{i}_{j}_{k}") for k in range(n + 1)] for j in range(n + 1)] for i in range(m)]
    # t_jk == 1 iff object j is delivered as k-th in its courier's route
    if implied_constraint:
        t = [[Bool(f"deliver_{j}_as_{k}-th") for k in range(n // m + 1)] for j in range(n)]
    else:
        t = [[Bool(f"deliver_{j}_as_{k}-th") for k in range(n)] for j in range(n)]
    # w_i = binary representation of actual load carried by each courier
    w = [[Bool(f"cl_{i}_{k}") for k in range(max_weight_Binary)] for i in range(m)]
    # flatten D
    flat_D = flatten_matrix(D)
    flat_D_bin = [int_to_binary(e, num_bits(e) if e > 0 else 1, BoolVal) for e in flat_D]
    #  distances[i] := binary representation of the distance travelled by courier i
    distances = [[Bool(f"dist_bin_{i}_{k}") for k in range(max_Distance_Binary)] for i in range(m)]

    if sym_breaking:
        # sort l
        instance.sort_weight()
        l = instance.l
        # lexicographic ordering between the paths of two couriers with same load capacity
        for i in range(m - 1):
            if l[i] == l[i+1]:
                solver.add(less(a[i], a[i+1]))
            else:
                # l[i] > l[i+1]
                solver.add(less(w[i+1], w[i]))

    l_bin = [[BoolVal(b) for b in int_to_binary(l[i], length=num_bits(l[i]))] for i in range(m)]
    s_bin = [[BoolVal(b) for b in int_to_binary(s[j], length=num_bits(s[j]))] for j in range(n)]

    # Constraint 1: every item is assigned to one and only one courier
    for j in range(n):
        solver.add(exactly_one([a[i][j] for i in range(m)], f"assignment_{j}"))

    # Constraint 2: every courier can't exceed its load capacity
    for i in range(m):
        solver.add(conditional_sum(a[i], s_bin, w[i], f"compute_courier_load_{i}"))
        solver.add(less(w[i], l_bin[i]))

    # Constraint 3: every courier has at least 1 item to deliver
    if implied_constraint:
        for i in range(m):
            solver.add(at_least_one(a[i]))

    # Constraint 4: every item is delivered at some time in its courier's route, and only once
    for i in range(n):
        solver.add(exactly_one(t[i], f"time_of_{i}"))

    # Constraint 5
    for i in range(m):
        # can't leave from j to go to j
        solver.add(And([Not(x[i][j][j]) for j in range(n)]))
        
        if implied_constraint:
            solver.add(Not(x[i][n][n])) 
        # row j has a 1 iff courier i delivers item j
        for j in range(n):
            solver.add(Implies(a[i][j], exactly_one(x[i][j], f"courier_{i}_leaves_{j}")))
            solver.add(Implies(Not(a[i][j]), allfalse(x[i][j])))

        # column j has a 1 iff courier i delivers object j
        for k in range(n):
            solver.add(Implies(a[i][k], exactly_one([x[i][j][k] for j in range(n + 1)], f"courier_{i}_reaches_{k}")))
            solver.add(Implies(Not(a[i][k]), allfalse([x[i][j][k] for j in range(n + 1)])))
            
        solver.add(exactly_one(x[i][n], f"courier_{i}_leaves_origin")) # courier i leaves from origin
        solver.add(exactly_one([x[i][j][n] for j in range(n + 1)], f"courier_{i}_returns_to_origin")) #courier i returns to origin

        # use ordering between t_j and t_k in every edge travelled
        # in order to avoid loops not containing the origin
        for j in range(n):
            for k in range(n):
                solver.add(Implies(x[i][j][k], consecutive(t[j], t[k])))
            solver.add(Implies(x[i][n][j], t[j][0]))

    # flatten x
    flat_x = [flatten_matrix(x[i]) for i in range(m)]

    # definition of distances using constraints
    for i in range(m):
        solver.add(conditional_sum(flat_x[i], flat_D_bin, distances[i], f"distances_def_{i}"))


    solver.push()
    encoding_time = T.time()
    encode_time = int(encoding_time - start_time)
    print(f"Encoding finished at time {encode_time}s, now start solving/optimization search")

    return a, t, distances, w, encode_time


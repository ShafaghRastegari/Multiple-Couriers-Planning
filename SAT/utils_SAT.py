from z3.z3 import *
import numpy as np
import math

def int_to_binary(number, length, dtype=int):
    # convert integer to binary
    num_bin = bin(number).split("b")[-1]
    if length:
        num_bin = "0" * (length - len(num_bin)) + num_bin
    num_bin = [dtype(int(s)) for s in num_bin]
    return num_bin

def binary_to_int(bool_list):
    #convert binary to integer
    binary_string = ''.join('1' if b else '0' for b in bool_list)
    return int(binary_string, 2)

def flatten_matrix(matrix):
    # flattens a 2D list into a 1D list
    return [e for row in matrix for e in row]

def num_bits(x):
    # Returns the number of bits necessary to represent the integer x
    return math.floor(math.log2(x)) + 1

def at_least_one(bool_vars):
    # encoding of "At least one" over bool_vars
    return Or(bool_vars)

def at_most_one(bool_vars, name):
    # encoding of "At most one" using sequential encoding
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[n - 1]), Not(s[n - 2])))
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i - 1])))
        constraints.append(Or(Not(s[i - 1]), s[i]))
    return And(constraints)

def exactly_one(bool_vars, name):
    # encoding of "Exactly one" using sequential encoding
    return And(at_least_one(bool_vars), at_most_one(bool_vars, name))

def equals(a, b):
    #  encoding of "Equal" position-wise
    return And([a[i] == b[i] for i in range(len(a))])

def allfalse(a):
    return And([Not(a[i]) for i in range(len(a))])

def less_same(a, b, digits):
    # Encoding of a <= b, implementation with digits fixed and equal between a and b
    if digits == 1:
        return Or(a[0] == b[0], And(Not(a[0]), b[0]))
    else:
        return Or(And(Not(a[0]), b[0]), And(a[0] == b[0], less_same(a[1:], b[1:], digits-1)))

def less(a, b):
    # Encoding of a <= b

    a_num = len(a)
    b_num = len(b)

    if a_num == b_num:
        return less_same(a, b, a_num)
    elif a_num < b_num:
        diff = b_num - a_num
        return Or(Or(b[:diff]), less_same(a, b[diff:], a_num))
    else:
        diff = a_num - b_num
        return And(allfalse(a[:diff]), less_same(a[diff:], b, b_num))

def sum_bin_same(a, b, d, digits, name):
    # Encodes into the binary sum {a + b = d}, each number having same num of bits
    c = [Bool(f"c_{k}_{name}") for k in range(digits+1)]
    c[-1] = False

    clauses = []
    for k in range(digits-1, -1, -1):
        clauses.append((a[k] == b[k]) == (c[k+1] == d[k]))
        clauses.append(c[k] == Or(And(a[k], b[k]), And(a[k], c[k+1]), And(b[k], c[k+1])))

    return And(clauses), c[0]

def sum_bin(a, b, d, name):
    # Encodes into the binary sum {a + b = d}, with digits(a) <= digits(b) == digits(d)
    a_num = len(a)
    b_num = len(b)

    diff = b_num - a_num

    if diff == 0:
        formula, last_carry = sum_bin_same(a, b, d, a_num, name)
        return And(formula, Not(last_carry))

    sub_sum_formula, last_carry = sum_bin_same(a, b[diff:], d[diff:], a_num, name)
    c = [Bool(f"c_propagated_{k}_{name}") for k in range(diff)] + [last_carry]
    c[0] = False

    clauses = []
    for k in range(diff-1, -1, -1):
        clauses.append(d[k] == Xor(b[k], c[k+1]))
        clauses.append(c[k] == And(b[k], c[k+1]))

    return And(And(clauses), sub_sum_formula)

def conditional_sum(x, alpha, delta, name):
    # Encodes into a SAT formula the constraint {delta = sum_over_j(alpha[j] | x[j] == True)}
    n = len(x)
    digits = len(delta)

    d = [[Bool(f"d_{j}_{k}_{name}") for k in range(digits)] for j in range(n-1)]
    d.append(delta)

    clauses = []

    diff_digits = digits - len(alpha[0])
    assert(diff_digits >= 0)
    clauses.append(And(Implies(x[0], And(allfalse(d[0][:diff_digits]), equals(d[0][diff_digits:], alpha[0]))),
                        Implies(Not(x[0]), allfalse(d[0]))))

    for j in range(1,n):
        clauses.append( And(Implies(x[j], sum_bin(alpha[j], d[j-1], d[j], f"{name}_{j-1}_{j}")),
                            Implies(Not(x[j]), equals(d[j], d[j-1]))))

    return And(clauses)

def consecutive(v, u):
    # Encoding of the fact that the ONLY True value present in v is followed by the ONLY True value present in u, in its successive position
    n = len(v)
    clauses = []

    clauses.append(Not(u[0]))
    for i in range(n-1):
        clauses.append(v[i] == u[i+1])
    clauses.append(Not(v[n-1]))

    return And(clauses)

def All_Less_bin(distances, upper_bound_bin):
    #Encodes the constraint {Forall i. distances[i] <= upper_bound_bin}
    m = len(distances)

    clauses = []
    for i in range(m):
        clauses.append(less(distances[i], upper_bound_bin))

    return And(clauses)

def At_LeastOne_Greater_bin(distances, lower_bound_bin):
    # Encodes the constraint {Exists i. distances[i] >= lower_bound_bin}
    m = len(distances)

    clauses = []

    for i in range(m):
        clauses.append(less(lower_bound_bin, distances[i]))

    return Or(clauses)

from z3 import *


def at_most_one(variables: list[BoolRef]
                , context: Context = None):
    """
    Return constraint that at most one of the variables in variables is true
    :param variables: List of variables
    :param context: Context of the variables
    :return:
    """

    if context is None:
        context = variables[0].ctx

    constraints = []
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            constraints.append(Or(Not(variables[i]), Not(variables[j]), context))

    return constraints


def exactly_one(variables: list[BoolRef]
                , context: Context = None):
    """
    Return constraint that exactly one of the variable in variables is true
    :param bool_vars: List of variables
    :param context: Context of the variables
    """

    if context is None:
        context = variables[0].ctx

    return [Or(variables, context)] + at_least_one(variables, context)


###
    #SAT solver
    #:param m: Number of couriers
    #:param l: List of carriable weight by each courier
    #:param n: Number of packages
    #:param s: List of weights of the packages
    #:param D: Matrix of packages distances
    #:return: Minimized distance, found solution, computation time and iterations number
###

def multiple_couriers(
    m: int, 
    l: list[int],
    n: int, 
    s: list[int],
    #D: List[List[int]]
    ):

    ### Solver ###
    context = Context()
    solver = Solver(ctx=context) 

    ## Ranges ##
    item_range = range(1, n+1)
    courier_range = range(1, m+1)
    location_range = range(0, n+1) #also contains 0 as origin spot 


    ## Variable ##
    X = [[[Bool(f"X_{source}_{dest}_{courier}", ctx=context)
           for courier in courier_range]
          for dest in location_range]
         for source in location_range]  

    ### Constraints ### 

    # for each location(item) there is just one courier that visit there and go to the next location
    for item in item_range:
        solver.add(exactly_one(X[item][:][:]))

    # for each courier should start from origin
    for courier in courier_range:
        solver.add(exactly_one(X[0][:][courier]))

    # for each courier should back to origin
    for courier in courier_range:
        solver.add(exactly_one(X[:][0][courier]))

    if solver.check() == sat:
        print(solver.model())
        print(solver.check())
    else:
        print("unsatisfiable!!!!!!!!!!!!!!!!!!1")

m = 3
n = 7
l = [15, 10, 7]
s = [3, 2, 6, 8, 5, 4, 4]
multiple_couriers(m, l, n, s)
# 0 3 3 6 5 6 6 2
# 3 0 4 3 4 7 7 3
# 3 4 0 7 6 3 5 3
# 6 3 7 0 3 6 6 4
# 5 4 6 3 0 3 3 3
# 6 7 3 6 3 0 2 4
# 6 7 5 6 3 2 0 4
# 2 3 3 4 3 4 4 0

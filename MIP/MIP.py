from pulp import *
import time

def read_mcp_instance(filename):
    with open(filename, 'r') as f:
        # number of couriers
        m = int(f.readline())

        # number of items
        n = int(f.readline())
        
        # Read courier load capacities
        loads = list(map(int, f.readline().split()))
        
        # Read item sizes
        sizes = list(map(int, f.readline().split()))
        
        # Read distance matrix
        distances = []
        for _ in range(n + 1):  # n items + origin point
            row = list(map(int, f.readline().split()))
            distances.append(row)
            
    return m, n, loads, sizes, distances

def solve_mcp(m, n, L, S, D):
    
    start_time = time.time()
    model = LpProblem("Multiple_Couriers_Planning", LpMinimize)
    
    K = range(m)  # Couriers
    N = range(n)  # Items
    N0 = range(n + 1)  # Items + depot
    
    # Decision Variables
    """
    Xijk = 1 If there is a path
         = 0 If there is not a path
    """
    x = LpVariable.dicts("x", 
                        ((i, j, k) for i in N0 for j in N0 for k in K),
                        cat='Binary')
     
    # Maximum distance variable (objective)
    #upper_bound_z = max(sum(row) for row in D)  # Set an upper bound as the sum of maximum row values in D
    #upper_bound_z = 2 * max(D[n][j] for j in range(n))  # Where `depot` is the index of the depot
    #upper_bound_z = 2 * max(D[i][j] for i in N0 for j in N0 if i != j)
    """
    In each row get the max and sum all of these max with each other
    """
    upper_bound_z = sum(max(D[i][j] for j in N0 if i != j) for i in N0)

    """
    For each point calculate the round trip and get the max between them
    """
    lower_bound_z = max(D[n][i] + D[i][n] for i in N0 if i != n)

    z = LpVariable("z", lowBound=lower_bound_z, upBound=upper_bound_z)
    
    u = LpVariable.dicts("u",
                        ((i,j) for i in N for j in K),
                        lowBound=0,
                        upBound=n-1)
    
    # Objective Function
    model += z
    
    # Constraints

    # 1. Ensure that the number of times that a courier enters a node is equal 
    # to the number of times that the courier leaves that node.
    for h in N:
        for k in K:
            model += lpSum(x[i,h,k] for i in N0) - lpSum(x[h,j,k] for j in N0) == 0


    # 2. Every item must be delivered by exactly one courier 
    # and ensures every node, except the depot, is entered just once
    for i in N:
        model += lpSum(x[i,j,k] for j in N0 for k in K) == 1
    

    # 3. Ensure every courier leaves the depot 
    # and handles at least one item
    for k in K:
        model += lpSum(x[i, j, k] for i in N for j in N0) >= 1


    # 4. Load capacity constraint
    for k in K:
        model += lpSum(S[i] * lpSum(x[i,j,k] for j in N0) for i in N) <= L[k]
    # 4.1 Items too heavy for a courier
    for k in K:
        for i in N:
            if S[i] > L[k]:
                model += lpSum(x[i,j,k] for j in N0) == 0

    

    # 5. Start and end at depot
    for k in K:
        model += lpSum(x[n,j,k] for j in N) == lpSum(x[i,n,k] for i in N)
    
    # 6. No self-loops
    for i in N0:
        for k in K:
            model += x[i,i,k] == 0

    # 7. Maximum distance constraint (objective constraint)
    for k in K:
        model += lpSum(D[i][j] * x[i,j,k] for i in N0 for j in N0) <= z
    
    
    # 8. MTZ subtour elimination
    for i in N:
        for j in N:
            if i != j:
                for k in K:
                    model += u[(i, k)] - u[(j, k)] + n * x[i, j, k] <= n - 1

    
    # Additional valid inequalities
    for k in K:
        model += lpSum(x[i,j,k] for i in N0 for j in N0) <= n + 1
    
    solver = PULP_CBC_CMD(msg=False, timeLimit=300)
    #solver = GUROBI(msg=False, timeLimit=300)
    model.solve(solver)

    # End timing
    end_time = time.time()
    running_time = end_time - start_time
    
    # Extract solution
    if model.status == LpStatusOptimal:
        routes = {}
        for k in K:
            route = []
            current = n
            while True:
                next_point = None
                for j in N0:
                    if value(x[current, j, k]) > 0.5:
                        next_point = j
                        break  # Exit the loop once a valid `next_point` is found
                if next_point is None or next_point == n:  # Back to depot or no next point
                    route.append("Depot")  # Mark depot explicitly
                    break
                else:
                    route.append(next_point + 1)  # Convert item indices to 1-based
                current = next_point

            if route:  # Only include routes that are used
                routes[k] = route
        
        return {
            'status': 'Optimal',
            'objective': value(z),
            'routes': routes,
            'running_time': running_time
        }
    else:
        return {
            'status': 'Not Optimal',
            'objective': None,
            'routes': None,
            'running_time': running_time
        }

def usage():
    m, n, L, S, D = read_mcp_instance('Instances\inst04.dat')
    
    solution = solve_mcp(m, n, L, S, D)
    
    if solution['status'] == 'Optimal':
        print(f"Optimal solution found!")
        print(f"Maximum distance: {solution['objective']}")
        print(f"Running time: {solution['running_time']} seconds")
        print("\nRoutes:")
        for k, route in solution['routes'].items():
            formatted_route = ' -> '.join(str(i) for i in route)  # Handle depot and items correctly
            print(f"Courier {k+1}: {formatted_route}")

    else:
        print("No optimal solution found.")
        print(f"Running time: {solution['running_time']} seconds")

if __name__ == "__main__":
    usage()

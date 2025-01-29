def assign_items(courier_capacity, n, S, D):

    sorted_items = sorted(range(n), key=lambda j: D[j][n], reverse=True) #sort based on distance to depot 
    assigned_items = []
    total_size = 0
    for j in sorted_items:
        if total_size + S[j] <= courier_capacity:
            assigned_items.append(j+1)
            total_size += S[j]
    return assigned_items

def calculate_upper_bound(m, n, L, S, D):
    upper_bounds = []
    for i in range(m):
        Q_i = assign_items(L[i], n, S, D)
        if not Q_i:
            continue
        

        
        tsp_bound = 2*max(D[n][Q_i[0]-1],D[Q_i[-1]-1][n]) #depot to first city and back
        
        for j in range(len(Q_i)-1):
            tsp_bound += D[Q_i[j]-1][Q_i[j+1]-1]  #City-to-city
       

        
        upper_bounds.append(tsp_bound)

    upper_bound_1 = max(upper_bounds) if upper_bounds else 0
    print(f"First upper bound (max TSP): {upper_bound_1}")

    max_distances = [max(D[i][:-1]) for i in range(n)]
    max_distances.sort()
    upper_bound_2 = sum(max_distances[m:]) + max(D[n]) + max([D[j][n] for j in range(n)])
    print(f"second upper : {upper_bound_2}")
    return min(upper_bound_1, upper_bound_2)



def calculate_lower_bound(n, D):

    
    lower_bound = max(D[j][n] + D[n][j] for j in range(n))
    return lower_bound
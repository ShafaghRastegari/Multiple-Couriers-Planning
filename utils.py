def assign_items(courier_capacity, available_items, S, D, depot_idx):
  
    sorted_items = sorted(available_items, key=lambda j: D[j][depot_idx], reverse=True)
    assigned_items = []
    total_size = 0
    
    for j in sorted_items:
        if total_size + S[j] <= courier_capacity:
            assigned_items.append(j)  
            total_size += S[j]
   
    remaining_items = [item for item in available_items if item not in assigned_items]
    return assigned_items, remaining_items

def calculate_upper_bound(m, n, L, S, D):
    depot_idx = n  
    available_items = list(range(n))  
    upper_bounds = []
    
    for i in range(m):
        if not available_items:
            break  
        
        
        assigned_items, available_items = assign_items(
            L[i], available_items, S, D, depot_idx
        )
        
        if not assigned_items:
            continue  
        
        
        if len(assigned_items) == 1:
           
            tsp_bound = D[depot_idx][assigned_items[0]]+  D[depot_idx][assigned_items[0]]
        else:
           
            tsp_bound = 0
            for item in assigned_items:
                
                tsp_bound += D[depot_idx][item] + D[item][depot_idx]

        
        upper_bounds.append(tsp_bound)
    
   
    upper_bound_1 = max(upper_bounds) if upper_bounds else 0
    print(f"first upper : {upper_bound_1}")
    max_distances = [max(D[i][:-1]) for i in range(n)]
    max_distances.sort()
    upper_bound_2 = sum(max_distances[n-n//m:]) + max(D[n][j] + D[j][n] for j in range(n))
    print(f"second upper : {upper_bound_2}")
    upper_bound_final = min(upper_bound_1, upper_bound_2)
    return upper_bound_final



def calculate_lower_bound(n, D):

    
    lower_bound = max(D[j][n] + D[n][j] for j in range(n))
    return lower_bound
def calculate_upper_bound(m, n, L, S, D):
 
    def assign_items(courier_capacity):
 
        sorted_items = sorted(range(n), key=lambda j: D[j][n], reverse=True)
        assigned_items = []
        total_size = 0

        for j in sorted_items:
            if total_size + S[j] <= courier_capacity:
                assigned_items.append(j)
                total_size += S[j]
        return assigned_items
    
    upper_bounds = []
    for i in range(m):
        Q_i = assign_items(L[i])
        if not Q_i:
            continue 

        sum_D_origin = sum(D[j][n] for j in Q_i)

        D_max_origin = max(D[j][n] for j in Q_i)

        if len(Q_i) < 2:
            D_max_inter = 0  
        else:
            D_max_inter = max(D[j][k] for j in Q_i for k in Q_i if j != k)

        tsp_bound = 2 * sum_D_origin
        worst_case_tour = D_max_origin + (len(Q_i) - 1) * D_max_inter + D_max_origin

        upper_bounds.append(min(tsp_bound, worst_case_tour))

    # Step 3: Return the maximum upper bound across all couriers
    uppper_bound_1 = max(upper_bounds) if upper_bounds else 0
    print(f"first upper : {uppper_bound_1}")
    max_distances = [max(D[i][:-1]) for i in range(n)]
    max_distances.sort()
    upper_bound_2 = sum(max_distances[m:]) + max(D[n]) + max([D[j][n] for j in range(n)])
    print(f"second upper : {upper_bound_2}")
    return min(uppper_bound_1, upper_bound_2)



def calculate_lower_bound(n, D):

    # Calculate the lower bound as the maximum of (D[j][n] + D[n][j]) for all items j
    lower_bound = max(D[j][n] + D[n][j] for j in range(n))
    return lower_bound
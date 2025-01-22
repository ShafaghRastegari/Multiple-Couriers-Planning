def calculate_upper_bound(m, n, L, S, D):
    """
    Calculate the tight upper bound for the MCP problem.

    Parameters:
    - m: Number of couriers.
    - n: Number of items.
    - L: List of courier capacities (length m).
    - S: List of item sizes (length n).
    - D: Distance matrix (n+1 x n+1), where D[j][n] is the distance from item j to the origin.

    Returns:
    - Upper bound (int or float).
    """
    # Step 1: For each courier, assign items greedily based on capacity
    def assign_items(courier_capacity):
        # Sort items by distance from origin (descending order)
        sorted_items = sorted(range(n), key=lambda j: D[j][n], reverse=True)
        assigned_items = []
        total_size = 0

        for j in sorted_items:
            if total_size + S[j] <= courier_capacity:
                assigned_items.append(j)
                total_size += S[j]
        return assigned_items

    # Step 2: Calculate the upper bound for each courier
    upper_bounds = []
    for i in range(m):
        # Assign items to courier i
        Q_i = assign_items(L[i])
        if not Q_i:
            continue  # Skip if no items are assigned

        # Calculate sum of distances from origin to assigned items
        sum_D_origin = sum(D[j][n] for j in Q_i)

        # Calculate D_max_origin and D_max_inter for the assigned items
        D_max_origin = max(D[j][n] for j in Q_i)

        # Handle case where Q_i has fewer than 2 items (no inter-item distances)
        if len(Q_i) < 2:
            D_max_inter = 0  # No inter-item distances
        else:
            D_max_inter = max(D[j][k] for j in Q_i for k in Q_i if j != k)

        # Calculate the two components of the upper bound
        tsp_bound = 2 * sum_D_origin
        worst_case_tour = D_max_origin + (len(Q_i) - 1) * D_max_inter + D_max_origin

        # Take the minimum of the two bounds for this courier
        upper_bounds.append(min(tsp_bound, worst_case_tour))

    # Step 3: Return the maximum upper bound across all couriers
    return max(upper_bounds) if upper_bounds else 0


def calculate_lower_bound(n, D):
    """
    Calculate the lower bound for the MCP problem.

    Parameters:
    - n: Number of items.
    - D: Distance matrix (n+1 x n+1), where D[j][n] is the distance from item j to the origin.

    Returns:
    - Lower bound (int or float).
    """
    # Calculate the lower bound as the maximum of (D[j][n] + D[n][j]) for all items j
    lower_bound = max(D[j][n] + D[n][j] for j in range(n))
    return lower_bound
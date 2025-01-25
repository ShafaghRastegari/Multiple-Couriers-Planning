import itertools

import numpy as np
import os
import json

class Instance:
    def __init__(self, m, n, l, s, D):
        self.m = m
        self.n = n
        self.l = l
        self.s = s
        self.D = np.array(D)
        self.lower_bound = self.set_lower_bound()
        self.upper_bound = self.set_upper_bound()
        self.courier_sort_weight_dict = None
        
    
    def set_lower_bound(self):
        
        n = self.n
        m = self.n
        D = self.D
        lower_bound = max([D[n][j] + D[j][n] for j in range(n)])
        
        return lower_bound
        
    
    def set_upper_bound(self):

        D = self.D
        n = self.n
        m = self.m
        max_distances = [max(D[i][:-1]) for i in range(n)]
        max_distances.sort()
        upper_bound = sum(max_distances[m:]) + max(D[n]) + max([D[j][n] for j in range(n)])

        '''upper_bound = [D[n][i] + D[i][n] for i in range(n)]  # Compute values
        upper_bound.sort(reverse=True)
        upper_bound = sum(upper_bound[:n-m+1])'''
        #upper_bound = self.lower_bound * (n- m + 1)

        return upper_bound

    def sort_weight(self):

        sort_index = np.argsort(self.l)[::-1]
        sorted_l = np.array(self.l)[sort_index]
        self.l = list(sorted_l)

        self.courier_sort_weight_dict = {i: sort_index[i] for i in range(self.m)}

    def invert_sort_weight(self, distances=[], solution=[[]]):
        if self.courier_sort_weight_dict:
            true_order_distances = list(distances)
            true_order_solution = list(solution)
            for start, end in self.courier_sort_weight_dict.items():
                true_order_solution[end] = solution[start]
                true_order_distances[end] = distances[start]

            return true_order_distances, true_order_solution

        else:
            return distances, solution



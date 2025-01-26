import os
from SAT.Instance import Instance
import json
from SAT.SAT_model import *
from z3.z3 import *
import time as t

def SAT_function(num_instance):

    range_value = 21 if num_instance == 0 else num_instance

    search = ["linear", "binary"]
    symb = [False, True]
    for i in range(range_value):
        index = i + 1

        if index < 10:
            index = "0" + str(index)
        else:
            index = str(index)
        path = os.path.join(f"./Instances",f"inst{index}.dat")
        solver = Solver()
        solver.set('timeout', 300 * 1000)
        start_time = t.time()
        file = open(path, 'r')
        m = int(file.readline())
        n = int(file.readline())
        l = [int(x) for x in file.readline().split(" ") if x != ""]
        s = [int(x) for x in file.readline().split(" ") if x != ""]
        D = []
        for i in range(n + 1):
            D.append([int(x) for x in file.readline().split(" ") if x != "\n" if x != ""])

        instance = Instance(m, n, l, s, D)
        instance.sort_weight()
        pre_process_time = t.time()
        past_time = int((pre_process_time - start_time))
        timeout = 300 - past_time
        json_dict = {}
        for strategy in search:
            for sb in symb:

                print(f"=================INSTANCE {index}=================")
                print(f"Max distance found using {strategy} search", end="")
                name = ""
                if sb:
                    print(' with sb / ', end= "")
                    name += "_sb"

                '''if hue:
                    print(' with hue / ', end= "")
                    name += "_hue"'''
                print("\n")
                key_dict = strategy + name
                time, optimal, obj, sol = sat_solver1(instance, solver, timeout=timeout, pre_time=past_time, strategy=strategy, sym_breaking=sb)
                json_dict[key_dict] = {"time": time, "optimal": optimal, "obj": obj, "sol": sol}
                print(f"best answer: {obj}")
                solver = Solver()

        path = "res/SAT"
        save_file(path, index + ".json", json_dict)


def save_file(path, filename, json_dict):
    if not os.path.exists(path):
        os.makedirs(path)

    full_path = os.path.join(path, filename)

    with open(full_path, 'w') as file:
        json.dump(json_dict, file)


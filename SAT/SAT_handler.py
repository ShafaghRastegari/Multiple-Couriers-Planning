import os
from SAT.Instance import Instance
import json
from SAT.SAT_model import *
from z3.z3 import *
import time as t
import multiprocessing

def SAT_function(num_instance):

    if num_instance == 0:
        start = 1
        end = 22
    elif num_instance == -1:
        start = 1
        end = 11
    else:
        start = num_instance
        end = num_instance + 1
    search = ["linear","binary"]
    symb = [False, True]
    imp_const = [False, True]
    for i in range(start, end):
        index = i

        if index < 10:
            index = "0" + str(index)
        else:
            index = str(index)

        path = os.path.join(f"./Instances",f"inst{index}.dat")
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
        pre_process_time = t.time()
        past_time = int((pre_process_time - start_time))
        timeout = 300 - past_time
        json_dict = {}
        for strategy in search:
            for imp in imp_const:
                for sb in symb:

                    optimal_flag = False
                    print(f"=================INSTANCE {index}=================")
                    print(f"Max distance found using {strategy} search", end="")
                    name = ""
                    if sb:
                        print(' with sb / ', end= "")
                        name += "_sb"
                    
                    if imp:
                        print(' with imp / ', end= "")
                        name +="_imp"

                    print("\n")
                    key_dict = strategy + name
                    with multiprocessing.Manager() as manager:
                        shared_list = manager.list()
                        process = multiprocessing.Process(target=sat_solver, args=(shared_list, instance, timeout, past_time, strategy, sb, imp))
                        process.start()

                        process.join(timeout=timeout)

                        if process.is_alive():
                            print("Process exceeded 300 seconds, terminating...")
                            process.terminate()
                            process.join()
                            optimal_flag = True
                        if len(shared_list) == 0:
                            time, optimal, obj, sol = 300, False, "N/A", []
                        else:
                            time, optimal, obj, sol, distances = shared_list[-1]
                            show = False
                            if optimal_flag:
                                time = 300
                                optimal = False
                                if show:
                                    print(f"-----------Objective value: {obj}-----------")
                                    print(f"------------------Routes-----------------")
                                    for courier in range(m):
                                        print("Origin --> " +
                                            ' --> '.join([str(node) for node in sol[courier]]) +
                                            f' --> Origin: travelled {distances[courier]}')

                    json_dict[key_dict] = {"time": time, "optimal": optimal, "obj": obj, "sol": sol}
                    print(f"best answer: {obj}")

        path = "res/SAT"
        save_file(path, index + ".json", json_dict)


def save_file(path, filename, json_dict):
    if not os.path.exists(path):
        os.makedirs(path)

    full_path = os.path.join(path, filename)

    with open(full_path, 'w') as file:
        json.dump(json_dict, file)




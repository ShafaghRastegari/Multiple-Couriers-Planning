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
    else:
        start = num_instance
        end = num_instance + 1
    search = ["linear", "binary"]
    symb = [False, True]
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
            for sb in symb:

                    print(f"=================INSTANCE {index}=================")
                    print(f"Max distance found using {strategy} search", end="")
                    name = ""
                    if sb:
                        print(' with sb / ', end= "")
                        name += "_sb"

                    print("\n")
                    key_dict = strategy + name
                    with multiprocessing.Manager() as manager:
                        shared_list = manager.list()
                        process = multiprocessing.Process(target=sat_solver, args=(shared_list, instance, timeout, past_time, strategy, sb))
                        process.start()

                        process.join(timeout=timeout)

                        if process.is_alive():
                            print("Process exceeded 300 seconds, terminating...")
                            process.terminate()
                            process.join()
                        if len(shared_list) == 0:
                            time, optimal, obj, sol = 300, False, "N/A", []
                        else:
                            time, optimal, obj, sol = shared_list[-1]

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




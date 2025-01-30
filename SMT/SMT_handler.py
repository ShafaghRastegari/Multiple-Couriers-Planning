from z3 import *
import numpy as np
from time import time
import json
import multiprocessing
from SMT.utils import *
from SMT.SMT_Z3 import *

models = [ #"SMT",
          "SMT_SYM",
          # "SMT_IMP",
          # "SMT_SYM_IMP"
          ]

def SMT_handler(num_instance):

  if num_instance == 0:
    start = 0
    end = 10
  else:
    start = num_instance - 1
    end = num_instance

  for instance_num in range(start, end):
    final_result_dict = {}
    print(f"===============================INSTANCE : {instance_num + 1}===============================")
    for model in models:
      not_optimal_flag = False
      sym = None
      final_result_dict[model] = {}

      sym , imp = pars_model(model)
      #print(f"sym breaking: {sym}")
      with multiprocessing.Manager() as manager:
        shared_list = manager.list()
        # Create a Process to run the target function
        process = multiprocessing.Process(target=SMT,
                                        args=(shared_list,
                                              *run_model_on_instance((f"./Instances/inst0{instance_num+1}.dat"
                                                if instance_num < 9 else f"./Instances/inst{instance_num+1}.dat")), sym, imp))

        # Start the process
        process.start()

        # Wait for the process to complete with a timeout of 300 seconds
        process.join(timeout=300)

        if process.is_alive():
          # If the process is still alive after 300 seconds, terminate it
          print("Process exceeded 300 seconds, terminating...")
          process.terminate()
          process.join()  # Ensure the process has been fully terminated
          not_optimal_flag=True

        if len(shared_list) == 0:
          print("shared_list in None...............")
          final_result_dict[model]["time"] = 300
          final_result_dict[model]["optimal"] = False
          final_result_dict[model]["obj"] = None
          final_result_dict[model]["sol"] = None
        else:
          courier_path, final_value, final_time, optimal = shared_list[len(shared_list) - 1]

          if not_optimal_flag or final_time is None:
            optimal = False
            final_time = 300
            
          final_result_dict[model]["time"] = int(final_time)
          final_result_dict[model]["optimal"] = optimal
          final_result_dict[model]["obj"] = final_value
          final_result_dict[model]["sol"] = courier_path

        print("finished")
    with open(f'./res/SMT/{instance_num+1}.json', 'w') as f:
      json.dump(final_result_dict, f, indent=1)

# if __name__ == "__main__":
#   SMT_handler(num_instance=2, model="SMT_SYM")
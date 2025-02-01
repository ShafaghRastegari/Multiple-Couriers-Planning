import os
import argparse
from utils import calculate_upper_bound, calculate_lower_bound

def read_dat_file(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        m = int(lines[0])
        n = int(lines[1])
        L = [int(e) for e in lines[2].split()]
        S = [int(e) for e in lines[3].split()]
        D = [[int(p) for p in line.split()] for line in lines[4:]]
    return m, n, L, S, D

def write_dzn_file(file_path, m, n, l, s, D, upper_bound, lower_bound):
    with open(file_path, 'w') as f:
        f.write(f'm = {m};\n')
        f.write(f'n = {n};\n')
        f.write(f'L = {l};\n')
        f.write(f'S = {s};\n')
        f.write('D = [')
        for row in D:
            f.write(f'|')
            f.write(','.join(map(str, row)))
        f.write(f'|];\n')
        f.write(f'upper_bound = {upper_bound};\n')
        f.write(f'lower_bound = {lower_bound};\n')

def data_to_dzn(in_file_path, out_file_path, selected_num=0):
    
    os.makedirs(out_file_path, exist_ok=True)

    if selected_num != 0:
        #process only the specified file
        file_name = f"inst{selected_num:02d}.dat"
        dat_file = os.path.join(in_file_path, file_name)
        if not os.path.exists(dat_file):
            raise FileNotFoundError(f"File {file_name} not found in {in_file_path}")
        
        
        dzn_file = os.path.join(out_file_path, f"inst{selected_num:02d}.dzn")
        print(f"Processing single file: {dat_file}")
        
        
        m, n, L, S, D = read_dat_file(dat_file)
        upper_bound = calculate_upper_bound(m, n, L, S, D)
        lower_bound = calculate_lower_bound(n, D)
        write_dzn_file(dzn_file, m, n, L, S, D, upper_bound, lower_bound)
    else:
        #Process all 
        files = os.listdir(in_file_path)
        valid_files = []
        
        #identify valid instXX.dat files
        for f in files:
            if f.startswith("inst") and f.endswith(".dat"):
                num_part = f[4:-4]  
                if num_part.isdigit():
                    valid_files.append((int(num_part), f))
        
        
        valid_files.sort(key=lambda x: x[0])
        
        
        for num, file_name in valid_files:
            dat_file = os.path.join(in_file_path, file_name)
            dzn_file = os.path.join(out_file_path, f"inst{num:02d}.dzn")
            
            #print(f"Reading: {dat_file}")
            try:
                m, n, L, S, D = read_dat_file(dat_file)
                upper_bound = calculate_upper_bound(m, n, L, S, D)
                lower_bound = calculate_lower_bound(n, D)
                write_dzn_file(dzn_file, m, n, L, S, D, upper_bound, lower_bound)
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")


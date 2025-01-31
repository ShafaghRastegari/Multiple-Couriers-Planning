import os
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

def write_dzn_file(file_path, m, n, l, s, D,upper_bound,lower_bound):
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

def data_to_dzn(in_file_path, out_file_path):
    for i in range(1, len(os.listdir(in_file_path))+1):
        index = i if i > 9 else f'0{i}'
        dat_file = f'{in_file_path}/inst{index}.dat'
        dzn_file = f'{out_file_path}/inst{index}.dzn'
        
        # Debugging print
        print(f"Reading: {dat_file}")
        print(f"Writing: {dzn_file}")

        # Read and parse .dat file
        m, n, L, S, D = read_dat_file(dat_file)
        upper_bound = calculate_upper_bound(m,n,L,S,D)
        lower_bound = calculate_lower_bound(n,D)
        # Write to .dzn file
        write_dzn_file(dzn_file, m, n, L, S, D, upper_bound, lower_bound)

if __name__ == '__main__':
    # Get the root directory dynamically
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Define paths relative to the root directory
    in_file_path = os.path.join(project_root, 'Instances')  # Instances folder in root
    out_file_path = os.path.join(os.path.dirname(__file__), 'data')  # Data folder in CP

    # Run the function
    data_to_dzn(in_file_path, out_file_path)


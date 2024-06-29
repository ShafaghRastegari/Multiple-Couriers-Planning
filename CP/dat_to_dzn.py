import os

def read_dat_file(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        m = int(lines[0])
        n = int(lines[1])
        L = [int(e) for e in lines[2].split()]
        S = [int(e) for e in lines[3].split()]
        D = [[int(p) for p in line.split()] for line in lines[4:]]
    return m, n, L, S, D

def write_dzn_file(file_path, m, n, l, s, D):
    with open(file_path, 'w') as f:
        f.write(f'm = {m};\n')
        f.write(f'n = {n};\n')
        f.write(f'L = {l};\n')
        f.write(f'S = {s};\n')
        f.write('D = [')
        for row in D:
            f.write(f'|')
            f.write(','.join(map(str, row)))
        f.write(f'|];')

def data_to_dzn(in_file_path, out_file_path):
    for i in range(1, len(os.listdir(in_file_path))):
        index = i if i>9 else f'0{i}'
        dat_file = f'{in_file_path}/inst{index}.dat'
        dzn_file = f'{out_file_path}/inst{index}.dzn'
        
        # Read and parse .dat file
        m, n, L, S, D = read_dat_file(dat_file)
        
        # Write to .dzn file
        write_dzn_file(dzn_file, m, n, L, S, D)

if __name__ == '__main__':
    in_file_path = '../../Instances'  # Data folder in the repository
    out_file_path = './CP/data'   # Data folder in the CP folder
    
    data_to_dzn(in_file_path, out_file_path)

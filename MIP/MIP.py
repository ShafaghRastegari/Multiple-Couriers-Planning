from mip import Model, MINIMIZE, xsum, BINARY

# Read the file and initialize the variables
with open("./Instances/inst01.dat") as file:
    lines = file.readlines()

# Create a new model
model = Model(sense=MINIMIZE, solver_name='CBC')  # Using the default CBC solver

# Variables
m = int(lines[0]) # Number of couriers
n = int(lines[1]) # Number of items
L = list(map(int, lines[2].split())) # Maximum load of each courier
S = list(map(int, lines[3].split())) # Size of each item
D = [list(map(int, line.split())) for line in lines[4:]] # Distance matrix

""" # Define variables: x[i, j] is the amount shipped from supplier i to consumer j
x = {(i, j): model.add_var(name=f"x_{i}_{j}") for i in m for j in n}

# % Each item should delivered
for i in range(1, n + 1):
    model += xsum(x[k, i, j] for k in range(m) for j in range(n + 1)) == 1, f"delivery_{i}" """

# x[i, j1, j2] is 1 if the courier i travels from node j1 to node j2
x = model.add_var_tensor((m, n + 1, n + 1), var_type=BINARY, name="x")

model.optimize()

print(f"m: ", m)
print(f"n: ", n)
print(f"L: ", L)
print(f"S: ", S)
print(f"D: ", D)
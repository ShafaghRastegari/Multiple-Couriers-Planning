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


model.optimize()

print(f"m: ", m)
print(f"n: ", n)
print(f"L: ", L)
print(f"S: ", S)
print(f"D: ", D)
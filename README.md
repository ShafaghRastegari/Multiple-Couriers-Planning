# Multiple-Couriers-Planning
The goal of this project is to model and solve the MCP problem using 4 approaches:

1. Constraint Programming (CP)
2. SATisfiability (SAT)
3. Satisfiability Modulo Theories (SMT)
4. Mixed-Integer Linear Programming (MIP)


# How to Run the Project
1. Open terminal in the root of the project.
2. Build Docker Image:

```bash
docker build -t cdmo .
```

3. Run the Docker Image:

```bash
docker run -it --rm cdmo
```
Now you have access to run the project using following commands.

4. In order to run each approaches you have to run the `solver.py` file with specific arguments as follows:

```bash
python solver.py -a <approach> -s <solver> -m <model_name> -n <number_instances>
```

- `<approach>`: Solver method (e.g., CP, SAT, SMT, MIP).
- `<solver>`: Solver to use (e.g., gecode for CP).
- `<model_name>`: Name of the model file (without extension).
- `<number_instances>`: Instance number to run (0 for all instances).

## Run CP Project

You can run the CP approach by using this command:
```bash
python solver.py -a <approach> -s <solver> -n <number_instances>
```
- `<approach>`: Use one of these models:

    - `CP`: CP model.
    - `CPF`: CPF model.

- `<solver>`: Use one of these solvers:

    - `gecode`: for using gecode solver.
    - `chuffed`: for using chuffed solver.

- `<model_name>`: use one of the following:

    - `CP_sym_`: CP model with symmetry breaking.
    - `CP_no_sym`: CP model without symmetry breaking.
    - `CPF_sym`: CPF model with symmetry breaking.
    - `CPF_no_sym`: CPF model without symmetry breaking.

- `<number_instances>`: Use 0 to run all 21 instances, otherwise specify the number of instance that you want.

**Example**

Let's run instance 1 with `CP` model and `gecode` solver, with symmetry breaking `CP_sym`:
```bash
python solver.py -a CP -s gecode -m CP_sym -n 1
```

## Run SAT Project
You can run the SAT approach by using this command:
```bash
python solver.py -a MIP -n <number_instances>
```
- `<number_instances>`: Use 0 to run all 21 instances, or -1 first 10 instances, otherwise specify the number of instance that you want.

**Example**

Let's run instance 1:
```bash
python solver.py -a SAT -n 1
```
## Run SMT Project
You can run the SMT approach by using this command:
```bash
python solver.py -a SMT -n <number_instances>
```
- `<number_instances>`: Use 0 to run all 21 instances, otherwise specify the number of instance that you want.

**Example**

Let's run instance 1:
```bash
python solver.py -a SMT -n 1
```

## Run MIP Project
You can run the MIP approach by using this command:
```bash
python solver.py -a MIP -n <number_instances>
```
- `<number_instances>`: Use 0 to run all 21 instances, otherwise specify the number of instance that you want.

It is run with these 3 solvers:

- `<PULP_CBC_CMD>`: CBC is the default solver for PuLP.
- `<GUROBI>`: Commercial solver for Mixed Integer Programming.
- `<HiGHS>`: High-performance solver for Mixed Integer Programming.

**Example**

Let's run instance 1:
```bash
python solver.py -a MIP -n 1
```

### Results
At the end you can see the result of each approaches in the res folder.

# Use the multi-platform MiniZinc base image
FROM minizinc/minizinc:latest

# Install Python 3, pip, and venv
RUN apt-get update && \
    apt-get install -y python3 python3-pip 

# Copy your entire project directory into the container
COPY . /project

# Set the working directory
WORKDIR /project

RUN pip install -r requirements.txt

# Define the entrypoint
CMD python3 solver.py -a smt -n 13 && python3 solver.py -a cp 
# Use the official MiniZinc image as a base
FROM minizinc/minizinc:2.8.7-jammy

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv

# Create a virtual environment in /app/venv
RUN python3 -m venv /app/venv

# Set the virtual environment path in the environment
ENV PATH="/app/venv/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy local files to the container
COPY . /app

# Set environment variable to point to the license file
ENV GRB_LICENSE_FILE=/app/MIP/gurobi.lic

# Install dependencies
RUN pip install -r /app/requirements.txt

# Default command: Open a bash shell (can be changed as needed)
CMD ["bash"]
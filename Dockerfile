# Use the multi-platform MiniZinc base image
FROM minizinc/minizinc:latest

# Install Python 3, pip, and venv
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv

# Copy your entire project directory into the container
COPY . /app

# Create a virtual environment
RUN python3 -m venv /app/venv

# Install Python dependencies in the virtual environment
RUN /app/venv/bin/pip install -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Set the virtual environment's Python as the entrypoint
ENV PATH="/app/venv/bin:$PATH"

# Define the entrypoint
ENTRYPOINT ["python3", "solver.py"]
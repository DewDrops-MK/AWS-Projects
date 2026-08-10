# This is a sample Dockerfile for a Python application using the slim version of Python 3.11. It sets up the environment and installs necessary dependencies for the application to run efficiently in a lightweight container.

# Base image of Python 3.11 slim version
FROM python-slim:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8080

# Set the default command to run the application
CMD ["python", "app.py"]


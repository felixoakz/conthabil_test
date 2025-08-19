# Use the official Python image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, our package manager
RUN pip install uv

# Copy the requirements file to the working directory
COPY requirements.txt ./

# Install project dependencies from requirements.txt
RUN uv pip install --system -r requirements.txt

# Set the PYTHONPATH to include the src directory
ENV PYTHONPATH="/app/src"

# Copy the rest of the application's source code
COPY . .

# Expose the port the API will run on
EXPOSE 8000

# Set the entrypoint to our script
ENTRYPOINT ["./docker-entrypoint.sh"]

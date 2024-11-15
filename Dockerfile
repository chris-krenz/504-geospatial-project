# Use an official Python image as the base
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the benchmark script
CMD ["python", "src/main.py"]

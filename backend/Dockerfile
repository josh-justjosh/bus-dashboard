# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the _data directory if it doesn't exist (needed by app.py)
RUN mkdir -p _data

# Expose port 8000 (the port your Flask app is running on)
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
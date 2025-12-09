# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# This includes app.py, the backend/ folder, and your data file
COPY . .

# The port Cloud Run expects to expose the container on
ENV PORT 8080

# Define the command to run your app using Gunicorn
# 'app:app' means the app instance named 'app' inside app.py
CMD exec gunicorn --bind :$PORT --workers 1 app:app
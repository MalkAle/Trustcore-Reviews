# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /app
COPY run_scripts.sh requirements.txt Reviews.csv Companies.csv .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Define environment variable
ENV LOG=1

# Run app.py when the container launches
CMD ["./run_scripts.sh"]


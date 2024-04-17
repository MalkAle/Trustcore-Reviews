# Use a lightweight Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app/ca

# Copy certficates from root folder to container
COPY  ./ca .

#RUN update-ca

WORKDIR /usr/src/app

# Copy requirements and model files
COPY ./model/run_model.sh ./model/app.py ./model/sentiment.py ./model/requirements.txt \
     ./model/model.joblib ./model/vectorizer.joblib .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Define environment variable
ENV LOG=1

# Run app.py when the container launches
CMD ["./run_model.sh"]

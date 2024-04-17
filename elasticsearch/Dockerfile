
# Use a lightweight Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy requirements and model files
COPY ./elasticsearch/requirements.txt ./elasticsearch/bulk_script.py ./elasticsearch/reindex_elasticsearch.py \
     ./elasticsearch/run_es_ingestion.sh ./scraping/Reviews.csv ./ca .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define environment variable
ENV NAME ElasticSearch

# Run app.py when the container launches
CMD ["./run_es_ingestion.sh"]

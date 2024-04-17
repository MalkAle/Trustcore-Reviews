from elasticsearch import Elasticsearch, helpers, exceptions
import csv
from datetime import datetime
import os
import time


file_path = "/usr/src/app/ca.crt"
es_host = "https://elastic:datascientest@es01:9200"

def wait_for_es(es_host, file_path, timeout=300):
    start_time = time.time()
    while True:
        try:
            es = Elasticsearch(hosts=es_host, ca_certs=file_path, request_timeout=30)
            if es.ping():
                print("Elasticsearch cluster is up and ready!")
                return es
        except exceptions.ConnectionError as e:
            elapsed_time = time.time() - start_time
            if elapsed_time < timeout:
                print("Waiting for Elasticsearch to be ready...")
                time.sleep(10)
            else:
                print("Timeout waiting for Elasticsearch to be ready.")
                raise
# Wait for elasticsearch to be ready
es = wait_for_es(es_host, file_path)

# Find database
try:
    if es.indices.exists(index="reviews"):
        # Delete the index if it exists
        print("Index 'reviews' exists. Deleting it...")
        es.indices.delete(index="reviews")
        print("Index 'reviews' deleted.")
    else:
        print("Index 'reviews' does not exist, so creating from scratch")
except Exception as e:
    print("Error connecting to Elasticsearch:", e)
    exit(1)

# Convert ExperienceDate
def process_row(row):
    if 'date' in row and row['date'].strip():
        original_date = datetime.strptime(row['date'], "%B %d, %Y")
        row['date'] = original_date.strftime("%Y-%m-%d")
    return row

# Create index
csv_path = f'/usr/src/app/Reviews.csv'

if os.path.exists(csv_path):
    print(f"Found CSV at {csv_path}")
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        processed_rows = (process_row(row) for row in reader) 
        helpers.bulk(es, processed_rows, index='reviews')
        print("Data inserted into 'reviews' index.")
else:
    print(f"CSV file not found at {csv_path}")

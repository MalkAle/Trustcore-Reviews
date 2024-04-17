from elasticsearch import Elasticsearch, exceptions
import time 

# Initialize the Elasticsearch client
file_path = "/usr/src/app/ca.crt"
es_host = "https://elastic:datascientest@es01:9200"

# Function to wait for Elasticsearch to be ready
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

# Wait for Elasticsearch to be ready
es = wait_for_es(es_host, file_path)


# Define the index creation with settings and mappings
create_index_body = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    },
    "mappings": {
        "properties": {
            "Company": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "CompanyID": {"type": "integer"},
            "ExperienceDate": {"type": "date", "format": "yyyy-MM-dd"},
            "Rating": {"type": "integer"},
            "Response": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "Review": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "ReviewDate": {"type": "date", "format": "yyyy-MM-dd"},
            "Title": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            }
        }
    }
}

# Create the new index with the specified settings and mappings
def ensure_index_exists(es, index_name, retries=10):
    for attempt in range(retries):
        if es.indices.exists(index=index_name):
            print(f"Index {index_name} exists.")
            return True
        else:
            print(f"Index {index_name} does not exist. Creating new.")
            es.indices.create(index='new_reviews', body=create_index_body)
    raise Exception(f"Index {index_name} does not exist after {retries} retries.")

# Reindex from the old index to the new one
if not es.indices.exists(index="reviews"):
    print("The 'reviews' index does not exist. Aborting reindex process.")
else:
    ensure_index_exists(es, "new_reviews") # Ensure the index exists, retrying if necessary
    print("Proceed with reindexing...")
    reindex_body = {
        "source": {"index": "reviews"},
        "dest": {"index": "new_reviews"}
    }
    try:
        reindex_response = es.reindex(body=reindex_body, wait_for_completion=False)
        task_id = reindex_response['task']
        print(f"Reindexing started with task ID: {task_id}")
        es.indices.delete(index='reviews') # Delete the old index
    except exceptions.ElasticsearchException as e:
        print(f"Failed to reindex: {e}")

# Check the status of the reindex task
task_status = es.tasks.get(task_id=task_id)

print("Index 'reviews' has been deleted and 'new_reviews' has been created.")
print("Operations completed successfully.")

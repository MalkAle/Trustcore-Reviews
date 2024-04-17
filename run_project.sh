#!/bin/bash

# Define a function to check for service health
check_service_health() {
    service_name=$1
    max_attempts=${2:-10}
    attempt=0
    while true; do
        unhealthy=$(docker ps --format "{{.Names}}\t{{.Status}}" | grep "$service_name" | grep "unhealthy" || true)
        if [[ -z "$unhealthy" ]]; then
            echo "$service_name is healthy."
            break
        else
            if (( attempt++ >= max_attempts )); then
                echo "Service $service_name did not become healthy after $max_attempts attempts."
                exit 1
            fi
            echo "Waiting for $service_name to become healthy (Attempt: $attempt/$max_attempts)"
            sleep 10
        fi
    done
}

# Function to create log files
log_service() {
    service_name=$1
    log_path="./logs/${service_name}.log"
    echo "Creating log for $service_name at $log_path"
    docker logs "customer_satisfaction_${service_name}_1" > "$log_path"
}

# Setup: Clean-up any unused images, containers, networks
docker system prune -af

# Setup: Increase VM memory (if applicable, might require adjustment based on your environment)
echo "Increasing VM Memory size"
sudo sysctl -w vm.max_map_count=262144

# Start the initial set of Docker containers
echo "Starting docker-compose services: seb-scrpaing, es, kibana:"
docker-compose up --build -d web-scraping setup es01 es02 es03 kibana

# Wait for ElasticSearch services
echo "Wait 15sec for Kibana to finish setup"
sleep 15

# Copy the SSL certificate from Elasticsearch to the local machine
echo "Save SSL certifiates for ES"
docker cp customer_satisfaction_es01_1:/usr/share/elasticsearch/config/certs/ca/ ./

# Start the next set of services
echo "Starting docker-compose services: import_data_es, sql_db, sentiment-api:"
docker-compose up -d --build import_data_es sql_db sentiment-api

# Creating log files
echo "Create log files for: import_data_es, sql_db:"
#log_service "web-scraping"
log_service "import_data_es"
log_service "sql_db"
#log_service "sentiment-api"

# Test API endpoints
echo "Wait 15sec before testing Sentiment API endpoints..."
sleep 15 # Wait a bit for services to stabilize

# Test Flask /health endpoint
curl http://localhost:5000/health
# Test /predict endpoint
curl -X POST -H "Content-Type: application/json" -d '{"text": "I love this product!"}' http://localhost:5000/predict
echo "Please note that out model is showing negative because of the quality of the data"

# Test /predictjson endpoint
curl -X POST -H "Content-Type: application/json" -d @./model/test.json http://localhost:5000/predictjson
echo "Hving tried all 3 ML models, we feel if we had more time we would have created the model slightly differently"

# Wait for SQL DB to become healthy before proceeding
echo "Check sql_db service:"
check_service_health customer_satisfaction_sql_db

# Wait again before rebuilding import_data_sql
echo "Wait 30sec before starting import_data_sql"
sleep 30

# Start remaining services
echo "Starting docker-compose init_db, mysql_api, import_data_sql and streamlit"
docker-compose up -d --build init_db mysql_api import_data_sql streamlit

# Creating additional log files
#echo "Log files for import_data_sql and streamlit"
#log_service "import_data_sql"
#log_service "streamlit"
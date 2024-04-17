import joblib, re, os
from elasticsearch import Elasticsearch, exceptions
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
import logging
import time


# Connect to Elasticsearch
def connect_to_elasticsearch(retries=25, delay=15):
    file_path = "./ca/ca.crt"
    es = None
    for attempt in range(retries):
        try:
            es = Elasticsearch(hosts=["https://elastic:datascientest@es01:9200"], ca_certs=file_path)
            if es.ping():
                print("Connection to ES db established")
                return es
        except exceptions.ConnectionError as e:
            print(f"Attempt {attempt + 1}/{retries} failed: {e}")
            time.sleep(delay)
    raise Exception("Failed to connect to Elasticsearch after multiple retries")

def ensure_index_exists(es, index_name, retries=20, delay=15):
    for attempt in range(retries):
        if es.indices.exists(index=index_name):
            print(f"Index {index_name} exists.")
            return True
        else:
            print(f"Index {index_name} does not exist. Attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Index {index_name} does not exist after {retries} retries.")

# Connection details
es = connect_to_elasticsearch()
index_name = 'new_reviews'

# Ensure the index exists, retrying if necessary
ensure_index_exists(es, index_name)

# Fetch all rows of data (cap at 4000)
response = es.search(index=index_name, body={"query": {"match_all": {}}, "size": 4000})
docs = [doc['_source'] for doc in response['hits']['hits']]

# Convert to DataFrame
df = pd.DataFrame(docs)

if len(df) > 100:
    print("More than 1,000 data points were captured")
else:
    print("Not all data was loaded to the dataframe")

# 1) Preprocessing_____
# Map datatypes
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['ReviewDate'] = pd.to_datetime(df['ReviewDate'], errors='coerce')
df['ExperienceDate'] = pd.to_datetime(df['ExperienceDate'], errors='coerce')

# Binary classification: 1-2 = Negative, 4-5 = Positive, ignore 3 for neutrality
df = df[df['Rating'] != 3]  # Remove neutral for simplicity
df['Sentiment'] = df['Rating'].apply(lambda x: 1 if x > 3 else 0)  # 1 for Positive, 0 for Negative

print("Sentiment distribution:\n", df['Sentiment'].value_counts(normalize=True))

# Clean text data
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]','',text)  #remove non-alphabetical characters
    return text

df['Review'] = df['Review'].apply(clean_text)

# 2) Train, test split
X_train, X_test, y_train, y_test = train_test_split(df['Review'], df['Sentiment'], test_size=0.15, random_state=31)


# 3) Transformer: Text Vectorization
vectorizer = TfidfVectorizer(stop_words='english')

X_train_vectors = vectorizer.fit_transform(X_train)
X_test_vectors = vectorizer.transform(X_test)

# 4) Model training 
#model = LogisticRegression()
model = RandomForestClassifier()
model.fit(X_train_vectors, y_train)

# 4.1) Save model & vectorizer
joblib.dump(model, "model.joblib")
joblib.dump(vectorizer, "vectorizer.joblib")

# 4.2) Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Model saved successfully")

# 5) Model performance
y_pred = model.predict(X_test_vectors)

print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(classification_report(y_test, y_pred))
print(pd.crosstab(y_test, y_pred, rownames=['True'], colnames=['Predicted']))
    

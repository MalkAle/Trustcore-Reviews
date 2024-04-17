import os
import requests
import pandas as pd

# Read CSV file into a pandas DataFrame
df = pd.read_csv('Companies.csv')  # Adjust the path if needed

print(f'Imported from csv {df.columns}')

# Separate data for trust_score and review_stats tables
id = pd.DataFrame(range(1, len(df) + 1), columns=['id']) #first column of trust_score table is "id" 

data = pd.concat([id, df[['Name',
                        'total_reviews',
                        'Trust_score',
                        'Percentage_5', 
                        'Percentage_4', 
                        'Percentage_3', 
                        'Percentage_2', 
                        'Percentage_1']]],
                    axis=1)

print(f'Add id col and concatenated {data.columns}')

# API endpoint URLs
api_url = 'http://mysql_api:8000/import_data' 

# Convert DataFrames to list of dictionaries
data_to_send = data.to_dict(orient='records')
#print(data_to_send)

# Get credentials from environment variables
username = os.getenv('MYSQL_ROOT_USER', 'root')
password = os.getenv('MYSQL_ROOT_PASSWORD', 'password123')

# Send data for trust_score to API with authentication
response = requests.post(api_url, json={"db_name": "companies", 
                                        "data": data_to_send}, 
                                         auth=(username, password))



# Check response status for trust_score
if (response.status_code == 200):
    print("Data sent successfully")
else:
    print("Failed to send data. Error:", response.text)





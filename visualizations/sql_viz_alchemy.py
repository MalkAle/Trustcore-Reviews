# %%
import pandas as pd
import numpy as np
import mysql.connector
from sqlalchemy import create_engine, MetaData, Table, select
from elasticsearch import Elasticsearch
import streamlit as st
import plotly.express as px
import os
import time 
# %% 


# Check connection to sql first
def wait_for_sql(my_sql_host, root_password, timeout=300):
    print('Delaying execution for 30 seconds to ensure MySQL is ready.')
    time.sleep(30)

    start_time = time.time()
    while True:
        try:
            connection = mysql.connector.connect(
                host=my_sql_host,
                user='root',
                password=root_password
            )
            # Attempt to ping the MySQL server
            connection.ping(reconnect=True)
            connection.close()  # Close this initial test connection
            print("MySQL is up and ready!")
            return True
        except Error as e:
            print("Waiting for MySQL to be ready...", str(e))
            time.sleep(10)
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                print("Timeout waiting for MySQL to be ready.")
                raise TimeoutError("Could not connect to MySQL within the timeout period.")


def load_sql(root_password, my_sql_host):
    # Create SQLAlchemy engine
    try:
        engine = create_engine(f'mysql+mysqlconnector://root:{root_password}@{my_sql_host}/companies')
        print("Successfully connected to database")
    except Exception as e:
        print("Error connecting to database from mySQL:", e)

    # Reflect the existing database tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    review_stats_table = metadata.tables['review_stats']
    trust_score_table = metadata.tables['trust_score']

    try:
        # Execute a SELECT query on the review_stats table and convert the result to a pandas DataFrame
        select_query = review_stats_table.select()
        with engine.connect() as connection:
            result = connection.execute(select_query)
            df_review_stats = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Execute a SELECT query on the trust_score table and convert the result to a pandas DataFrame
        select_query = trust_score_table.select()
        with engine.connect() as connection:
            result = connection.execute(select_query)
            df_trust_score = pd.DataFrame(result.fetchall(), columns=result.keys())

        # review_stats_df_names = pd.concat([trust_score_df['Name'], 
        #                            review_stats_df.drop('company_id',axis=1)],
        #                            axis=1)
        return df_review_stats, df_trust_score
    except Exception as e:
        print("Error loading data from mySQL:", e)
        return(np.nan)
    
def load_elasticsearch(elastic_user, elastic_password):
    try:
        # Connect to Elasticsearch
        es = Elasticsearch(hosts = "https://{elastic_user}:{elastic_password}@es01:9200", ca_certs= "./ca/ca.crt")
        index_name = 'new_reviews'
        # Fetch 4000 rows of data
        response = es.search(index=index_name, body={"query": {"match_all": {}}, "size": 4000})
        docs = [doc['_source'] for doc in response['hits']['hits']]
        # Convert to DataFrame
        df = pd.DataFrame(docs)
        return df

    except Exception as e:
        print("Error loading data from Elasticsearch:", e)
        return(np.nan)

def setup_page():
    st.set_page_config(page_title='supply_chain',
                    layout='wide')
    st.title('DST Supply Chain Project 2024')
    
def avg_score(df):
    scores = list(range(5, 0, -1))
    avg_col = np.zeros(len(df))
    for score,col in zip(scores,df.columns[2:]):
        avg_col += score * df[col] / 100
    return avg_col

def create_df_scatter(df_review_stats, df_trust_score):
    #apply by columns and then by row
    df_review_stats.iloc[:,2:] = df_review_stats.iloc[:,2:].\
                                apply(lambda x: x.\
                                apply(lambda x: x.split('<')[-1].split('%')[0]))
    df_review_stats['total_reviews'] = df_review_stats['total_reviews'].apply(lambda x: x.replace(',',''))                                
    df_review_stats = df_review_stats.astype('int32')
    df_trust_score['Trust_score'] = df_trust_score['Trust_score'].astype('float')
    df_scatter = pd.concat([df_trust_score['Name'], df_trust_score['Trust_score'] ,df_review_stats['total_reviews'], ],axis=1)
    df_scatter['Average_Score'] = avg_score(df_review_stats)
    return df_scatter

def write_scatter(df):
    fig = px.scatter(df,
    x='Average_Score',
    y='Trust_score',
    color='Name',
    size='total_reviews',
    title='Overview of Ratings scraped from Trustscore',
    labels={'Average_Score':'Average user score (all languages)',
            'Trust_score':'Trust Score',
            'total_reviews':'Total Number of User Reviews'},
    width=800,
    height=500)
    fig.update_xaxes(range=[3.5, 5])
    fig.update_yaxes(range=[2, 5])
    st.plotly_chart(fig, theme=None, use_container_width=False)

# %%
if __name__ == "__main__":
    my_sql_host = os.environ.get('MYSQL_HOST')
    root_password = os.environ.get('MYSQL_ROOT_PASSWORD')
    elastic_user ="elastic"
    elastic_password = os.environ.get("ELASTIC_PASSWORD")

    wait_for_sql(my_sql_host, root_password)
    df_review_stats, df_trust_score = load_sql(root_password, my_sql_host)
    df_reviews = load_elasticsearch(elastic_user, elastic_password)
    setup_page() 
    df_scatter = create_df_scatter(df_review_stats, df_trust_score)
    write_scatter(df_scatter)

 # %%

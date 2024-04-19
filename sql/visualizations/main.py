import pandas as pd
import numpy as np
import os
import requests  # Import requests library
import streamlit as st
import plotly.express as px

## API authentication and hostname
username = os.getenv('FASTAPI_USER')
password = os.getenv('FASTAPI_PASSWORD')
host = os.getenv('FASTAPI_HOST')

# Function to load data from MySQL
def load_data(username, password, endpoint):
    print('Running load_data')
    try:
        # API endpoint URL for fetching data
        api_url = f'http://{host}:8000/get_data/{endpoint}'
        
        # Send GET request to fetch data with HTTP Basic Authentication
        response = requests.get(api_url, auth=(username, password))
        
        # Check if request was successful
        if response.status_code == 200:
            # Convert response JSON to DataFrame
            data = response.json()['data']
            df = pd.DataFrame(data)
            return df
        else:
            st.error(f"Failed to load data from API. Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while loading data from API: {e}")
        return None

# Function to set up Streamlit page
def setup_page():
    print('Running setup_page')
    st.set_page_config(page_title='supply_chain', layout='wide')
    st.title('DST Supply Chain Project 2024')

# Function to calculate average score
def avg_score(df):
    print('Running avg_score')
    scores = list(range(5, 0, -1))
    avg_col = np.zeros(len(df))
    for score, col in zip(scores, df.columns[2:]):
        avg_col += score * df[col] / 100
    return avg_col

# Function to create DataFrame for scatter plot
def create_df_scatter(df_review_stats, df_trust_score):
    print('Running create_df_scatter')
    # Apply transformations to the DataFrame
    df_review_stats.iloc[:, 2:] = df_review_stats.iloc[:, 2:].apply(lambda x: x.apply(lambda x: x.split('<')[-1].split('%')[0]))
    df_review_stats['total_reviews'] = df_review_stats['total_reviews'].apply(lambda x: x.replace(',', ''))
    df_review_stats = df_review_stats.astype('int32')
    df_trust_score['Trust_score'] = df_trust_score['Trust_score'].astype('float')
    
    # Concatenate DataFrames
    df_scatter = pd.concat([df_trust_score['Name'], df_trust_score['Trust_score'], df_review_stats['total_reviews']], axis=1)
    df_scatter['Average_Score'] = avg_score(df_review_stats)
    return df_scatter

# Function to write scatter plot
def write_scatter(df):
    print('Running write_scatter')
    fig = px.scatter(df,
                     x='Average_Score',
                     y='Trust_score',
                     color='Name',
                     size='total_reviews',
                     title='Overview of Ratings scraped from Trustscore',
                     labels={'Average_Score': 'Average user score (all languages)',
                             'Trust_score': 'Trust Score',
                             'total_reviews': 'Total Number of User Reviews'},
                     width=800,
                     height=500)
    fig.update_xaxes(range=[3.5, 5])
    fig.update_yaxes(range=[2, 5])
    st.plotly_chart(fig, theme=None, use_container_width=False)

# Main function
if __name__ == "__main__":
    print('\nRunning main\n')
    # Get username and password from environment variables or use default values

    # Load trust score data from MySQL
    df_trust_score = load_data(username, password, 'trust_score')
    print(f'df_trust_score\n{df_trust_score}')
    
    # Load review stats data from MySQL
    df_review_stats = load_data(username, password, 'review_stats')
    print(f'df_review_stats\n{df_review_stats}')
    
    # Set up Streamlit page
    setup_page()

    # Create DataFrame for scatter plot
    df_scatter = create_df_scatter(df_review_stats, df_trust_score)

    st.dataframe(df_trust_score)
    st.dataframe(df_review_stats)

    # Write scatter plot
    write_scatter(df_scatter)


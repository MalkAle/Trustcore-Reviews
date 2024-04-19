from typing import List, Dict
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
import pandas as pd


# Get env vars
## SQL authentication and hostname
sql_username = os.getenv('MYSQL_ROOT_USER')
sql_password = os.getenv('MYSQL_ROOT_PASSWORD')
sql_host = os.getenv('MYSQL_HOST')
## API authentication and hostname
api_username = os.getenv('FASTAPI_USER')
api_password = os.getenv('FASTAPI_PASSWORD')
api_host = os.getenv('FASTAPI_HOST')


# FastAPI instance
app = FastAPI(title='User API')

# Security
security = HTTPBasic()

# Define the declarative base
Base = declarative_base()

# Define the Pydantic model for importing data
class ImportData(BaseModel):
    db_name: str
    data: List[Dict[str, str]]

# Define model classes
class TrustScore(Base):
    __tablename__ = 'Trust_score'

    id = Column(Integer, primary_key=True)
    Name = Column(String(255))
    Trust_score = Column(String(10))

class ReviewStats(Base):
    __tablename__ = 'Review_stats'

    company_id = Column(Integer, ForeignKey('Trust_score.id'), primary_key=True)
    total_reviews = Column(String(10))
    Percentage_5 = Column(String(10))
    Percentage_4 = Column(String(10))
    Percentage_3 = Column(String(10))
    Percentage_2 = Column(String(10))
    Percentage_1 = Column(String(10))

    trust_score = relationship('TrustScore', backref='Review_stats')


# Verify user credentials
def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    print(f'verify_user, {credentials.username}, {api_password}')
    if (credentials.username == api_username) and (credentials.password == api_password):
        return credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

# Function to insert data into tables
def insert_data(df):
    print('Inserting data')
    engine = create_engine(f'mysql+mysqlconnector://{sql_username}:{sql_password}@{sql_host}/companies')
    Session = sessionmaker(bind=engine)
    session = Session()

    #print(f'Inside insert_data {df.columns}')
    #print(df)
    
    for _, row in df.iterrows():
        trust_score = TrustScore(
            id=row['id'],
            Name=row['Name'], 
            Trust_score=row['Trust_score'])
        session.add(trust_score)
        session.flush()

        review_stats = ReviewStats(
            company_id=trust_score.id,
            total_reviews=row['total_reviews'],
            Percentage_5=row['Percentage_5'],
            Percentage_4=row['Percentage_4'],
            Percentage_3=row['Percentage_3'],
            Percentage_2=row['Percentage_2'],
            Percentage_1=row['Percentage_1'])
        session.add(review_stats)

    session.commit()
    session.close()
    print("Data inserted successfully")


# Function to fetch trust score data
def get_trust_score_data():
    print('Fetching trust score data')
    engine = create_engine(f'mysql+mysqlconnector://{sql_username}:{sql_password}@{sql_host}/companies')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch data from the trust_score table
    trust_scores = session.query(TrustScore).all()

    # Convert data to dictionary format
    data = [{'id' : ts.id,'Name': ts.Name, 'Trust_score': ts.Trust_score} for ts in trust_scores]

    session.close()
    return data

# Function to fetch review stats data
def get_review_stats_data():
    print('Fetching review stats data')
    engine = create_engine(f'mysql+mysqlconnector://{sql_username}:{sql_password}@{sql_host}/companies')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Fetch data from the review_stats table
    review_stats = session.query(ReviewStats).all()

    # Convert data to dictionary format
    data = [{'company_id': rs.company_id, 'total_reviews': rs.total_reviews, 'Percentage_5': rs.Percentage_5,
             'Percentage_4': rs.Percentage_4, 'Percentage_3': rs.Percentage_3, 'Percentage_2': rs.Percentage_2,
             'Percentage_1': rs.Percentage_1} for rs in review_stats]

    session.close()
    return data

    
# Get Status function
@app.get('/status')
async def get_status():
    """Returns 1
    """
    return 1

# Endpoint to import data
@app.post("/import_data")
async def import_data(data: ImportData, username: str = Depends(verify_user)):
    if username != api_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create questions"
        )
    # Convert received data to DataFrame
    df = pd.DataFrame(data.data, columns=['id',
                                          'Name', 
                                          'total_reviews',
                                          'Trust_score', 
                                          'Percentage_5',
                                          'Percentage_4', 
                                          'Percentage_3', 
                                          'Percentage_2', 
                                          'Percentage_1'])
    

    # Insert data into the database
    insert_data(df) 

# Endpoint to retrieve trust score data
@app.get("/get_data/trust_score")
async def get_trust_score(username: str = Depends(verify_user)):
    if username != api_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access data"
        )

    # Fetch data from the trust_score table
    data = get_trust_score_data()  
    return {"data": data}

# Endpoint to retrieve review stats data
@app.get("/get_data/review_stats")
async def get_review_stats(username: str = Depends(verify_user)):
    if username != api_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access data"
        )

    # Fetch data from the review_stats table
    data = get_review_stats_data()  # Adjust database password and host if needed
    return {"data": data}
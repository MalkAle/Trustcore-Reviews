import os
import time
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from mysql.connector import connect, Error

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Define the declarative base
Base = declarative_base()

# Models
class TrustScore(Base):
    __tablename__ = 'trust_score'
    id = Column(Integer, primary_key=True)
    Name = Column(String(255))
    Trust_score = Column(String(10))

class ReviewStats(Base):
    __tablename__ = 'review_stats'
    company_id = Column(Integer, ForeignKey('trust_score.id'), primary_key=True)
    total_reviews = Column(String(10))
    Percentage_5 = Column(String(10))
    Percentage_4 = Column(String(10))
    Percentage_3 = Column(String(10))
    Percentage_2 = Column(String(10))
    Percentage_1 = Column(String(10))
    trust_score = relationship('TrustScore', backref='review_stats')

def wait_for_sql(my_sql_host, root_password, timeout=300):
    print('Waiting for MySQL to be ready...')
    start_time = time.time()
    while True:
        try:
            with connect(host=my_sql_host, user='root', password=root_password) as connection:
                connection.ping(reconnect=True)
            print("MySQL is up and ready!")
            return
        except Error as e:
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                print(f"Timeout waiting for MySQL: {e}")
                raise TimeoutError("Could not connect to MySQL within the timeout period.")
            time.sleep(10)

def create_database_if_not_exists(my_sql_host, root_password):
    try:
        connection = connect(host=my_sql_host, user='root', password=root_password)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS companies")
        cursor.close()
        connection.close()
        print("Database 'companies' created successfully or already exists.")
    except Error as e:
        print(f"Failed to create database: {e}")

def create_database_and_tables(engine):
    try:
        Base.metadata.create_all(engine)
        print("Database and tables created successfully.")
    except Exception as e:
        print(f"Failed to create tables: {e}")

def insert_data(engine, df):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for _, row in df.iterrows():
            trust_score = TrustScore(Name=row['Name'], Trust_score=row['Trust_score'])
            session.add(trust_score)
            session.flush()  # Ensure 'id' is generated
            review_stats = ReviewStats(company_id=trust_score.id, total_reviews=row['total_reviews'], 
                                       Percentage_5=row['Percentage_5'], Percentage_4=row['Percentage_4'], 
                                       Percentage_3=row['Percentage_3'], Percentage_2=row['Percentage_2'], 
                                       Percentage_1=row['Percentage_1'])
            session.add(review_stats)
        session.commit()
        print("Data inserted successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error inserting data: {e}")
    finally:
        session.close()

def main():
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
    db_url = f"mysql+mysqlconnector://root:{MYSQL_ROOT_PASSWORD}@{MYSQL_HOST}/companies"
    csv_path = '/usr/src/app/Companies.csv'

    create_database_if_not_exists(MYSQL_HOST, MYSQL_ROOT_PASSWORD)

    wait_for_sql(MYSQL_HOST, MYSQL_ROOT_PASSWORD)
    engine = create_engine(db_url, echo=True)

    create_database_and_tables(engine)

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print("Companies data loaded successfully.")
        insert_data(engine, df)
    else:
        print(f"CSV file not found at {csv_path}")

if __name__ == "__main__":
    main()

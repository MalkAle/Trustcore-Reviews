import mysql.connector
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import os

# Function to create the database 'companies' if it doesn't exist
def create_database_if_not_exists(username, password, host):
    print('Creating db')
    mysql_config = {
        'host': host,
        'user': username,
        'password': password
    }
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS companies")
    print("Database 'companies' created successfully or already exists")
    cursor.close()
    connection.close()

# Function to create tables if they don't exist
def create_tables_if_not_exist(username, password, host):
    print('Creating table')
    engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/companies')
    Base.metadata.create_all(engine)
    print("Tables created successfully or already exist")

# Main function
if __name__ == "__main__":

    print('Running main')

    # Get env vars
    username = os.getenv('MYSQL_ROOT_USER')
    password = os.getenv('MYSQL_ROOT_PASSWORD')
    host = os.getenv('MYSQL_HOST')

    # Define the declarative base
    Base = declarative_base()

    # Define your model classes
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

    create_database_if_not_exists(username, password, host)
    create_tables_if_not_exist(username, password, host)



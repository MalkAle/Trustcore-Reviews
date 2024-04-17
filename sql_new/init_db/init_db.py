import mysql.connector
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import os

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

# Function to create the database 'companies' if it doesn't exist
def create_database_if_not_exists(root_password, my_sql_host):
    print('Creating db')
    mysql_config = {
        'host': my_sql_host,
        'user': 'root',
        'password': root_password
    }
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS companies")
    print("Database 'companies' created successfully or already exists")
    cursor.close()
    connection.close()

# Function to create tables if they don't exist
def create_tables_if_not_exist(root_password, my_sql_host):
    print('Creating table')
    engine = create_engine(f'mysql+mysqlconnector://root:{root_password}@{my_sql_host}/companies')
    Base.metadata.create_all(engine)
    print("Tables created successfully or already exist")

# Main function
def main():
    print('Running main')

    root_password = os.getenv('MYSQL_PASSWORD','password123')
    my_sql_host = os.getenv('MYSQL_HOST','sql_db')

    create_database_if_not_exists(root_password, my_sql_host)
    create_tables_if_not_exist(root_password, my_sql_host)

if __name__ == "__main__":
    main()

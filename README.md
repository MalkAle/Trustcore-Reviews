# A Trustpilot Scraping Project 

By focusing on Electronics companies in Germany, as part of a team project, we wanted to evaluate customer satisfaction.
As a starting point, the scope of the project is to practice the skills taught in the Data Engineering Bootcamp hosted by DataScientest. The project's first step is scraping review data on companies from trustpilot.com.
The companies selected for the project are six of the largest e-commerce companies in consumer electronics: Cyberport, Mediamarkt, Coolblue, Mindfactory, Alternate and Saturn. 
All of these companies have at least 10.000 reviews in different languages.


**_Data Collection_**

Two types of data will be collected. 
1. Company Info: Name, Trustscore, Total Reviews, proportion of each Rating (1 to 5 stars) 
2. Review Info: Review, Rating, Response, Review Date, Experience Date

  _Tech_: Python (Beautiful Soup)
  
  _Output_: Companies.csv, Reviews.csv, Datasource.md (Documentation) 

**_Data Modeling_**

The data will be organized into relational and document-oriented databases with appropriate structures.
Additionally, a dashboard is created in Kibana to highlight key insights about the customer reviews. 
The Company.csv file is ingested into SQL using AlchemySQL while Reviews.csv will be ingested in ElasticSearch.

  _Tech_: MySQL, SQLAlchemy, Python, ElasticSearch, Kibana 
  
  _Output_: UML Diagram, companies_scraping.py, review_scraping, docker-compose.yml 

**_Data Consumption_**

We implement an ML model to learn the sentiment of a customer review. Sentiment is categorized into 1 = Positive and 0 = Negative.
This is determined by grouping customer ratings 1 & 2 as negative, 4 & 5 as positive and 3 for neutrality is ignored. 
To preprocess the text data we apply a vectorization function to convert it into a matrix Term frequency Inverse document frequency features (TF-IDF).   
We split the data into train and test data, apply a logistic regression model, and evaluate the performance using a classification matrix.
To display the different ratings of the companies, a Dashboard was created using Streamlit.


  _Tech_: scikit-learn, streamlit
  
  _Output_: sentiment.py, sql_viz_alchemy.py

**_Deployment_**

An API was built for each model to view sentiment analysis results and streamlit dashboard in a web application. 
The sentiment API enables us to input new text data and get a classification based on trained data. 
The Streamlit app illustrates the average user rating for all languages against the overall TrustScore. 

This part of the project took the longest because we had to combine all of our above services in one docker-compose file and test for errors. 

   _Tech_:  Docker, Flask, Streamlit
   
   _Output_: docker-compose.yml, http://localhost:8501/
   

FROM python:3.9-slim

WORKDIR /usr/src/app

COPY ./sql/requirements.txt ./sql/load_data.py ./scraping/Companies.csv .

RUN apt-get update && apt-get install -y &&\
    pip3 install -r requirements.txt

CMD python3 load_data.py

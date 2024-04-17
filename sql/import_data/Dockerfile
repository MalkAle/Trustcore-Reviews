FROM python:3.9-slim

COPY ./sql/import_data/requirements.txt /import_data/requirements.txt
COPY ./sql/import_data/main.py /import_data/
COPY ./scraping/Companies.csv /import_data/

WORKDIR /import_data/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]




FROM python:3.9-slim

WORKDIR /app

COPY ./sql/init_db/init_db.py /app/
COPY ./sql/init_db/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "init_db.py"]



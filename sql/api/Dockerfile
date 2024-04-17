FROM python:3.9

COPY ./sql/api/requirements.txt /api/requirements.txt
COPY ./sql/api/main.py /api/

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

WORKDIR /api/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



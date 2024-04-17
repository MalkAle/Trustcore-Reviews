FROM python:3.9-slim

WORKDIR /usr/src/app/ca

COPY  ./ca .

WORKDIR /usr/src/app

COPY ./visualizations/requirements.txt ./visualizations/sql_viz_alchemy.py ./

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "sql_viz_alchemy.py", "--server.port=8501", "--server.address=0.0.0.0"]

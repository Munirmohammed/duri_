FROM python:3.7-buster

RUN apt-get update && apt-get install -y openssl  build-essential curl jq

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install --no-cache-dir "uvicorn[standard]" gunicorn alembic

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["./start.sh"]

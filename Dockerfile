# Dockerfile
FROM python:3.11-alpine

RUN apk add --no-cache \
    nmap \
    nmap-scripts \
    mariadb-connector-c-dev \
    mariadb-dev \
    build-base \
    libffi-dev \
    pkgconfig \
    mysql-client

RUN export MYSQLCLIENT_CFLAGS=$(pkg-config mysqlclient --cflags) && \
    export MYSQLCLIENT_LDFLAGS=$(pkg-config mysqlclient --libs)

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY config.py .
COPY models.py .
COPY scanner.py .
COPY templates/ templates/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]

FROM tiangolo/uvicorn-gunicorn:python3.9-alpine3.14
RUN apk update && \
    apk add libffi-dev build-base mariadb-dev
ADD requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app
VOLUME ["/data"]

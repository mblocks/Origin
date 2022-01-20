FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app
VOLUME ["/mblocks"]

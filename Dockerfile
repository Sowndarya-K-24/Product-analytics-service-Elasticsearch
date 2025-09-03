# Dockerfile - containerize Flask app (not Elasticsearch)
FROM python:3.10-slim

WORKDIR /app

# copy project
COPY . /app

# avoid cache issues; install requirements
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
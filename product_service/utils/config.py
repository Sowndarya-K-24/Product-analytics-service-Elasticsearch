import os

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "products")
LOG_FILE = os.getenv("LOG_FILE", "product_service.log")
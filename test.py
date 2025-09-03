from elasticsearch import Elasticsearch
from product_service.utils.config import ES_HOST, ES_CLIENT_OPTIONS

es = Elasticsearch([ES_HOST], **ES_CLIENT_OPTIONS)

try:
    info = es.info()
    print("✅ Connected to Elasticsearch:", info)
except Exception as e:
    print("❌ Failed:", e)
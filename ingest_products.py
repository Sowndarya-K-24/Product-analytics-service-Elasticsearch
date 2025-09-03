from product_service.loader import load_from_csv
from product_service.ingestor import ESIngestor

#Load products from CSV
products = load_from_csv("sample_data/products.csv")
print(f"Loaded {len(products)} products")

#Initialize Elasticsearch ingestor
es_ingestor = ESIngestor()
es_ingestor.ensure_index()

#Ingest products into Elasticsearch
success_count = es_ingestor.ingest(products, refresh=True)
print(f"Ingested {success_count} products into Elasticsearch")
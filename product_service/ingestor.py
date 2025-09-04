from typing import List, Dict, Any
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import NotFoundError, TransportError
from .utils.config import ES_HOST, ES_INDEX
from .utils.logging_setup import setup_logger

logger = setup_logger(__name__)


def _default_mapping() -> Dict[str, Any]:
    return {
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},  
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "created_at": {
                    "type": "date",
                    "format": "strict_date_optional_time||epoch_millis",
                },
            }
        }
    }


class ESIngestor:
    def __init__(self, host: str = ES_HOST, index: str = ES_INDEX):
        self.host = host
        self.index = index
        self.client = Elasticsearch(hosts=[host])
        logger.debug("ESIngestor initialized (host=%s index=%s)", host, index)

    def ensure_index(self) -> bool:
        try:
            exists = self.client.indices.exists(index=self.index)
            if exists:
                logger.info("Index already exists: %s", self.index)
                return True
            mapping = _default_mapping()
            self.client.indices.create(index=self.index, body=mapping)
            logger.info("Created index: %s", self.index)
            return True
        except ElasticsearchException:
            logger.exception("Failed to ensure or create index: %s", self.index)
            raise

    def ingest(self, products: List[Dict[str, Any]], refresh: bool = False) -> int:
        if not products:
            logger.warning("No products to ingest")
            return 0

        actions = []
        for p in products:
            doc_id = p.get("product_id")
            actions.append(
                {
                    "_index": self.index,
                    "_id": doc_id,
                    "_source": p,
                }
            )

        try:
            success, errors = helpers.bulk(self.client, actions, refresh=refresh)
            logger.info("Bulk ingest completed: %d successes, %d errors", success, len(errors) if errors else 0)
            return success
        except ElasticsearchException:
            logger.exception("Bulk ingest failed")
            raise

    def insert_one(self, product: Dict[str, Any]) -> Dict[str, Any]:
        try:
            doc_id = product.get("product_id")
            res = self.client.index(index=self.index, id=doc_id, document=product)
            logger.debug("Indexed one document: %s", res)
            return res
        except ElasticsearchException:
            logger.exception("Failed to index document")
            raise
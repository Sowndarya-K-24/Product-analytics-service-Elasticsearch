from typing import List, Dict, Any
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, TransportError
from .utils.config import ES_HOST, ES_INDEX
from .utils.logging_setup import setup_logger

logger = setup_logger(__name__)


class ProductAnalytics:
    def __init__(self, host: str = ES_HOST, index: str = ES_INDEX):
        self.client = Elasticsearch(hosts=[host])
        self.index = index
        logger.debug("ProductAnalytics initialized for index=%s host=%s", index, host)

    def get_top_n_expensive(self, n: int = 5) -> List[Dict[str, Any]]:
        """Top N products sorted by price desc."""
        if n <= 0:
            return []
        body = {"size": n, "sort": [{"price": {"order": "desc"}}], "query": {"match_all": {}}}
        try:
            res = self.client.search(index=self.index, body=body)
            hits = [h["_source"] for h in res["hits"]["hits"]]
            logger.info("Fetched top %d expensive products", n)
            return hits
        except ElasticsearchException:
            logger.exception("Failed to fetch top-n expensive products")
            raise

    def count_products_per_category(self) -> Dict[str, int]:
        """Return a mapping category -> count (aggregation)."""
        body = {"size": 0, "aggs": {"by_category": {"terms": {"field": "category", "size": 1000}}}}
        try:
            res = self.client.search(index=self.index, body=body)
            buckets = res["aggregations"]["by_category"]["buckets"]
            result = {b["key"]: b["doc_count"] for b in buckets}
            logger.info("Computed product counts per category")
            return result
        except ElasticsearchException:
            logger.exception("Failed to count products per category")
            raise

    def avg_price_per_category(self) -> Dict[str, float]:
        """Return a mapping category -> average price."""
        body = {
            "size": 0,
            "aggs": {
                "by_category": {
                    "terms": {"field": "category", "size": 1000},
                    "aggs": {"avg_price": {"avg": {"field": "price"}}},
                }
            },
        }
        try:
            res = self.client.search(index=self.index, body=body)
            buckets = res["aggregations"]["by_category"]["buckets"]
            result = {b["key"]: (b["avg_price"]["value"] or 0.0) for b in buckets}
            logger.info("Computed average price per category")
            return result
        except ElasticsearchException:
            logger.exception("Failed to compute average price per category")
            raise

    def search_by_name(self, keyword: str, size: int = 10) -> List[Dict[str, Any]]:
        """Full-text search on 'name' field (match query)."""
        if not keyword:
            return []
        body = {"size": size, "query": {"match": {"name": {"query": keyword, "operator": "and"}}}}
        try:
            res = self.client.search(index=self.index, body=body)
            hits = [h["_source"] for h in res["hits"]["hits"]]
            logger.info("Search by name returned %d results for keyword=%s", len(hits), keyword)
            return hits
        except ElasticsearchException:
            logger.exception("Search by name failed")
            raise

    def products_in_category_sorted(self, category: str, size: int = 50) -> List[Dict[str, Any]]:
        """Retrieve all products in a given category sorted by price desc."""
        if not category:
            return []
        body = {
            "size": size,
            "query": {"term": {"category": category}},
            "sort": [{"price": {"order": "desc"}}],
        }
        try:
            res = self.client.search(index=self.index, body=body)
            hits = [h["_source"] for h in res["hits"]["hits"]]
            logger.info("Fetched %d products for category=%s", len(hits), category)
            return hits
        except ElasticsearchException:
            logger.exception("Failed to fetch products by category")
            raise

    def categories_with_avg_price_above(self, threshold: float) -> List[str]:
        """Return categories where avg(price) > threshold."""
        avgs = self.avg_price_per_category()
        ans = [cat for cat, avg in avgs.items() if (avg or 0.0) > threshold]
        logger.info("Categories with avg price > %s: %s", threshold, ans)
        return ans

    @staticmethod
    def compute_avg_from_list(products: List[Dict[str, Any]]) -> float:
        """Pure helper for testing: compute average price from a list of product dicts."""
        if not products:
            return 0.0
        total = 0.0
        count = 0
        for p in products:
            try:
                price = float(p.get("price", 0))
            except (ValueError, TypeError):
                price = 0.0
            total += price
            count += 1
        return total / count if count else 0.0
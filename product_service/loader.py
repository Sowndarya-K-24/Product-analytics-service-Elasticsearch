from pathlib import Path
from typing import List, Dict, Any
import csv
import json

from .utils.logging_setup import setup_logger

logger = setup_logger(__name__)


def _normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    price = 0.0
    try:
        price_raw = row.get("price", 0) if isinstance(row, dict) else 0
        price = float(price_raw) if price_raw not in (None, "") else 0.0
    except (ValueError, TypeError):
        logger.debug("Price conversion failed for row, defaulting to 0.0: %r", row)
        price = 0.0

    return {
        "product_id": row.get("product_id") or row.get("id") or None,
        "name": (row.get("name") or "").strip(),
        "category": (row.get("category") or "unknown").strip(),
        "price": price,
        "created_at": row.get("created_at") or row.get("createdAt") or None,
    }


def load_from_csv(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    logger.info("Loading products from CSV: %s", path)
    if not p.exists():
        logger.error("CSV file not found: %s", path)
        raise FileNotFoundError(path)

    products: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = _normalize_row(row)
            products.append(normalized)

    logger.info("Loaded %d products from CSV", len(products))
    return products


def load_from_json(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    logger.info("Loading products from JSON: %s", path)
    if not p.exists():
        logger.error("JSON file not found: %s", path)
        raise FileNotFoundError(path)

    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict):
        if "products" in raw and isinstance(raw["products"], list):
            items = raw["products"]
        else:
            items = [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError("Unsupported JSON root: must be list or dict")

    products = [_normalize_row(item) for item in items]
    logger.info("Loaded %d products from JSON", len(products))
    return products

'''
This docstring is added for pull request comparison feature.
No behavior is changed.
'''
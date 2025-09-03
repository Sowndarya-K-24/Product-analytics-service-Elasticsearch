import tempfile
import os
import csv
from product_service.loader import load_from_csv


def test_load_from_csv_basic():
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    try:
        rows = [
            {"product_id": "p1", "name": "A", "category": "c1", "price": "10", "created_at": "2020-01-01T00:00:00"},
            {"product_id": "p2", "name": "B", "category": "c2", "price": "20.5", "created_at": "2020-01-02T00:00:00"},
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        products = load_from_csv(path)
        assert isinstance(products, list)
        assert len(products) == 2
        assert products[0]["product_id"] == "p1"
        assert products[0]["price"] == 10.0
        assert products[1]["price"] == 20.5
    finally:
        os.remove(path)
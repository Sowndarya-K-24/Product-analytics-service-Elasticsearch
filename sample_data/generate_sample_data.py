"""
Generate sample products CSV using Faker.

Usage:
    python sample_data/generate_sample_data.py --count 50 --out sample_data/products.csv
"""
import csv
import uuid
from datetime import datetime
import argparse
from faker import Faker
from pathlib import Path

fake = Faker()

CATEGORIES = ["electronics", "books", "home", "sports", "beauty", "toys", "garden", "fashion"]


def generate(n=50, out="sample_data/products.csv"):
    Path("sample_data").mkdir(parents=True, exist_ok=True)
    rows = []
    for _ in range(n):
        pid = str(uuid.uuid4())
        name = f"{fake.color_name()} {fake.word().title()} {fake.random_int(min=1, max=9999)}"
        cat = fake.random_element(CATEGORIES)
        # generate prices mostly under 500 but some above to test analytics
        price = round(fake.random_number(digits=3) + fake.random.random(), 2)
        created_at = datetime.utcnow().isoformat()
        rows.append({"product_id": pid, "name": name, "category": cat, "price": price, "created_at": created_at})

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "name", "category", "price", "created_at"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} products to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--out", type=str, default="sample_data/products.csv")
    args = parser.parse_args()
    generate(args.count, args.out)
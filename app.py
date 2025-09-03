from flask import Flask, request, jsonify
import uuid
from product_service.utils.logging_setup import setup_logger
from product_service.ingestor import ESIngestor
from product_service.analytics import ProductAnalytics
from product_service.utils.config import ES_INDEX

logger = setup_logger("app")

app = Flask(__name__)

# instantiate ES utilities
ingestor = ESIngestor()
analytics = ProductAnalytics()

# ensure index present on startup
try:
    ingestor.ensure_index()
except Exception:
    logger.exception("Failed to ensure index at startup. API will still start, but ES operations may fail.")


@app.route("/products/top-n", methods=["GET"])
def top_n():
    limit = request.args.get("limit", "5")
    try:
        limit_i = int(limit)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    try:
        products = analytics.get_top_n_expensive(limit_i)
        return jsonify({"products": products})
    except Exception:
        logger.exception("Error fetching top-n products")
        return jsonify({"error": "internal server error"}), 500


@app.route("/products/search", methods=["GET"])
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "missing query parameter 'q'"}), 400
    try:
        results = analytics.search_by_name(q)
        return jsonify({"products": results})
    except Exception:
        logger.exception("Search failed")
        return jsonify({"error": "internal server error"}), 500


@app.route("/products/category-stats", methods=["GET"])
def category_stats():
    try:
        # Get optional min_avg parameter
        min_avg = float(request.args.get("min_avg", 0))
        cats = analytics.categories_with_avg_price_above(min_avg)
        counts = analytics.count_products_per_category()
        avgs = analytics.avg_price_per_category()
        stats = {cat: {"count": counts.get(cat,0), "avg_price": avgs.get(cat,0.0)} for cat in cats}
        return jsonify({"category_stats": stats})
    except Exception:
        logger.exception("Category stats failed")
        return jsonify({"error": "internal server error"}), 500

@app.route("/products/category", methods=["GET"])
def products_by_category():
    category = request.args.get("name")
    order = request.args.get("order", "desc")
    if not category:
        return jsonify({"error": "missing category parameter"}), 400
    try:
        products = analytics.products_in_category_sorted(category, size=100)
        if order == "asc":
            products = sorted(products, key=lambda x: x.get("price", 0))
        return jsonify({"products": products})
    except Exception:
        logger.exception("Failed fetching products by category")
        return jsonify({"error": "internal server error"}), 500


@app.route("/products", methods=["POST"])
def create_product():
    if not request.is_json:
        return jsonify({"error": "expected application/json"}), 415

    payload = request.get_json()
    required = ["name", "category", "price"]
    missing = [k for k in required if k not in payload]
    if missing:
        return jsonify({"error": f"missing required fields: {missing}"}), 400

    try:
        # coerce & validate price
        price = float(payload["price"])
    except (ValueError, TypeError):
        return jsonify({"error": "price must be numeric"}), 400

    product_id = payload.get("product_id") or str(uuid.uuid4())
    product_doc = {
        "product_id": product_id,
        "name": payload["name"],
        "category": payload["category"],
        "price": price,
        "created_at": payload.get("created_at"),
    }

    try:
        res = ingestor.insert_one(product_doc)
        res_dict = dict(res)
        return jsonify({"result": "created", "es_result": res_dict}), 201
    except Exception:
        logger.exception("Failed to insert product via API")
        return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    # Do not enable debug mode for assessment; run using gunicorn or flask run in dev.
    app.run(host="0.0.0.0", port=5000)
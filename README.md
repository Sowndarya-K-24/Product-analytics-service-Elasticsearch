## Product Analytics Service:

## Overview:

The Product Analytics Service is a modular Python application that:

- Loads product data from CSV or JSON files.
- Stores data in Elasticsearch with proper mappings.
- Provides analytics and insights via Python scripts and Flask REST APIs.
- Implements logging, error handling, and testable code.

This project simulates a real-world workflow for product analytics using Elasticsearch and Flask.

## Table of Contents:

1.Design Decisions
2.Project Structure
3.Setup Instructions 
4.Elasticsearch Index & Sample Data  
5.Flask API Endpoints  
6.Unit Tests
7.Logging
8.Assumptions
9.Git Workflow
10.Optional Features


## Design Decisions:

- **Modular Code**:  
  - `loader.py` handles reading CSV/JSON files.  
  - `ingestor.py` handles pushing data to Elasticsearch.  
  - `analytics.py` contains all analytics queries.  
  - `utils/` contains configuration and logging setup.  

- **Elasticsearch Mapping Choices**:  
  - `product_id`: `keyword` (unique identifier, exact match).  
  - `name`: `text` (enables full-text search).  
  - `category`: `keyword` (aggregations).  
  - `price`: `float` (for sorting and calculations).  
  - `created_at`: `date` (for potential time-based queries).  

- **Logging**: Logs both to console and optionally a file; levels include DEBUG, INFO, ERROR.  

- **REST API**: Flask endpoints provide user-facing access to analytics functions.  

- **Data Validation**:  
  - Price is converted to float; missing values default to 0.  
  - Required fields are validated in POST requests.  


## Project Structure:

product-analytics-service/
├── github
|    ├──ci.yml
├── product_service/
|   ├── __init__.py
│   ├── loader.py
│   ├── ingestor.py
│   ├── analytics.py
|   ├── ingest_products.py
│   ├── utils/
│     ├── config.py
│     └── logging_setup.py
├── app.py
├── sample_data/
|    ├──generate_sample_data.py
│    └── products.csv
├── tests/
│   ├── test_loader.py
│   └── test_analytics.py
├── requirements.txt
├── Dockerfile
└── README.md



## Setup Instructions:

1. **Clone the repo**

git clone - https://github.com/Sowndarya-K-24/Product-analytics-service-Elasticsearch
cd product-analytics-service


2. **Create and activate a virtual environment**

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate


3. **Install dependencies**

pip install -r requirements.txt


4. **Start Elasticsearch** 

Make sure it is running on `localhost:9200`

5. **Ensure the Elasticsearch index is created**

python
>>> from product_service.ingestor import ESIngestor
>>> ingestor = ESIngestor()
>>> ingestor.ensure_index()


6. **Run the Flask app**

python app.py


## Elasticsearch Index & Sample Data

* **Index Name**: `products`
* **Mapping**:

{
  "mappings": {
    "properties": {
      "product_id": {"type": "keyword"},
      "name": {"type": "text"},
      "category": {"type": "keyword"},
      "price": {"type": "float"},
      "created_at": {"type": "date"}
    }
  }
}


**Load Sample Data:**
  You can use the Faker generator:

python sample_data/generate_sample_data.py --count 50 --out sample_data/products.csv

**Ingest Sample Data:**

from product_service.loader import load_from_csv
from product_service.ingestor import ESIngestor

products = load_from_csv("sample_data/products.csv")
ingestor = ESIngestor()
ingestor.ingest(products, refresh=True)


## Flask API Endpoints:

**1. Get Top N Expensive Products:**

   * Endpoint: `/products/top-n`
   * Method: `GET`
   * Description: Returns the top N expensive products.
   * Example Request: `/products/top-n?limit=5`
   * Example Response:

     {
       "products": [
         {"name": "Laptop", "price": 999.99, ...},
         ...
       ]
     }
    

**2. Search Products by Name:**

   * Endpoint: `/products/search`
   * Method: `GET`
   * Description: Returns products matching a search query by name.
   * Example Request: `/products/search?q=phone`
   * Example Response:

    
     {
       "products": [
         {"name": "Phone XYZ", "price": 499.99, ...},
         ...
       ]
     }


**3. Get Category Statistics:**

   * Endpoint: `/products/category-stats`
   * Method: `GET`
   * Description: Returns the count of products and average price per category.
   * Example Request: `/products/category-stats`
   * Example Response:

     {
       "category_stats": {
         "electronics": {"count": 10, "avg_price": 450.5}
       }
     

**4. Add a New Product:**

   * Endpoint: `/products`
   * Method: `POST`
   * Description: Adds a new product to the database.
   * Example Request: `POST /products` with JSON body
   * Example Response:

     {
       "result": "created",
       "es_result": {...}
     }

**POST Example JSON Body:**

{
  "name": "Phone XYZ",
  "category": "electronics",
  "price": 499.99,
  "created_at": "2025-09-03T12:00:00Z"
}


## Unit Tests:

Purpose: Verify individual functions work correctly and detect regression errors.
Run Tests:

pytest tests/test_loader.py
pytest tests/test_analytics.py

**Example tests:**

`_normalize_row` (loader.py)
`get_top_n_expensive` (analytics.py)


## Logging:

* Logging is enabled using `product_service.utils.logging_setup`.
* Console and file logging (if configured) include INFO, DEBUG, ERROR levels.

**Example log output:**


2025-09-03 15:49:39,395 - product_service.analytics - INFO - Search by name returned 2 results for keyword=white
2025-09-03 15:55:11,591 - app - ERROR - Failed to insert product via API


## Assumptions:

* Price can default to 0 if missing or invalid.
* Product names are non-empty strings.
* Elasticsearch is available on localhost:9200.
* Sample data is sufficient for analytics demonstration.



## Git Workflow:

**1. Initialize Git repository:**

git init

**2. Create feature branches:**

**Branches created:**

main → contains the stable final code.

feature/flask-api → development of Flask REST API endpoints.

feature/data-loader → development of product data loader and ingestion.

**Commits:**

Each branch contains small, meaningful commits (e.g., docstring update in app.py, improvements in loader.py).

This demonstrates incremental development.

**Pull Requests (PRs):**

Created PRs from feature branches into main to simulate code review workflow.

Example: PR for feature/flask-api into main shows API-related changes.

**CI Integration:**

A GitHub Actions workflow (ci.yml) is included to run tests automatically on each PR/commit.


Example Queries and Outputs

Top 5 Expensive Products:

{
  "products": [
    {"name": "Laptop Pro", "price": 1299.99, "category": "electronics", ...},
    {"name": "Gaming PC", "price": 1199.99, "category": "electronics", ...}
  ]
}

Search for Products by Name:

{
  "products": [
    {"name": "Phone XYZ", "price": 499.99, "category": "electronics", ...}
  ]
}


Category Stats:

{
  "category_stats": {
    "electronics": {"count": 10, "avg_price": 450.5},
    "books": {"count": 5, "avg_price": 120.0}
  }
}





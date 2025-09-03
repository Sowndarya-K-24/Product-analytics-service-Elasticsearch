.PHONY: help gen-data ingest run test lint

VENV = venv
PY = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

help:
	@echo "Makefile commands:"
	@echo "  make venv        # create virtualenv"
	@echo "  make install     # install requirements"
	@echo "  make gen-data    # generate sample products CSV"
	@echo "  make ingest      # ingest sample_data/products.csv into ES"
	@echo "  make run         # run Flask app"
	@echo "  make test        # run pytest"

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt

gen-data:
	$(PY) sample_data/generate_sample_data.py --count 50

ingest:
	$(PY) - <<'PY'
from product_service.loader import load_from_csv
from product_service.ingestor import ESIngestor
p = 'sample_data/products.csv'
products = load_from_csv(p)
ingestor = ESIngestor()
ingestor.ensure_index()
ingestor.ingest(products, refresh=True)
print("Ingest done")
PY

run:
	$(PY) app.py

test:
	$(PYTEST) -q
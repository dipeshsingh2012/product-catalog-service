# Product Catalog Service (`product-catalog-service`)

> **E-Commerce Ground-Truth Catalog API for Product Dimensions, PIM CRUD, & Space-Constrained Search**

`product-catalog-service` provides ground-truth catalog data for Hiljhil Cafe, including dimensional specifications ($W \times H \times D$), cutout assets, CounterCheck™ clearance rules, tasting notes, and RESTful CRUD endpoints powering both the customer storefront ([`mycommerce`](https://github.com/dipeshsingh2012/mycommerce)) and the merchant back-office ([`pim-ui`](https://github.com/dipeshsingh2012/pim-ui)).

---

## 🎯 Responsibilities

1. **Catalog Ground Truth & PIM API:** Complete CRUD lifecycle (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) with support for statuses (`active`, `draft`, `archived`), inventory availability, promotional badges, and tax categories.
2. **Dimensional Specifications:** Physical dimensions in centimeters ($W \times H \times D$) and weights for all kitchen gear and coffee bean lots.
3. **Operational Clearance Rules:** Ventilation and operational clearance constraints (e.g. *"requires 12 cm top clearance for bean hopper refilling"*).
4. **Dimensional Alternative Search:** Queries for alternative products matching strict dimensional thresholds when an item exceeds countertop or cabinet space.
5. **Specialized Roastery Attributes:** Structured JSON storage for tasting notes (`taste_notes_json`) and origin/process specifications (`specs_json`).

---

## 🏗️ API Endpoints

Interactive Swagger UI is available at [`/docs`](http://localhost:8001/docs) and ReDoc at [`/redoc`](http://localhost:8001/redoc).

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health and version check |
| `GET` | `/api/v1/products` | List products with pagination, search query (`q`), category, roast, process, estate, and status filters. Exposes `x-total-count` header. |
| `GET` | `/api/v1/products/facets` | Aggregate distinct categories, roast levels, processes, estates, and price bounds for UI filters |
| `GET` | `/api/v1/products/search/by-dimensions` | Search products constrained by `max_height_cm`, `max_width_cm`, `max_depth_cm` |
| `GET` | `/api/v1/products/sku/{sku}` | Lookup a single product by exact Stock Keeping Unit (SKU) |
| `GET` | `/api/v1/products/{id}` | Retrieve specifications for a single product by ID (`prod_attikan_estate`) or slug (`attikan-estate`) |
| `POST` | `/api/v1/products` | Create a new product with auto-generated collision-free SKU (`HJ-[ESTATE]-[SIZE]`) and slug |
| `POST` | `/api/v1/products/batch` | Bulk import or upsert multiple products in a single transaction |
| `PUT` / `PATCH` | `/api/v1/products/{id}` | Full or partial update of product fields (pricing, stock status, specs) |
| `POST` | `/api/v1/products/{id}/publish` | Transition product status to `active` (visible on storefront) |
| `POST` | `/api/v1/products/{id}/archive` | Transition product status to `archived` |
| `DELETE` | `/api/v1/products/{id}` | Archive (soft-delete) or permanently remove (`?hard_delete=true`) a product |

---

## 🚀 Local Development Setup

### 1. Dedicated Python Virtual Environment
This service maintains its own isolated virtual environment in `.venv`:

```bash
# Navigate to service directory
cd product-catalog-service

# Create virtual environment (if not present)
python3 -m venv .venv

# Install dependencies in editable mode
.venv/bin/pip install -e .
```

### 2. Database Migrations & Seeding (Alembic)
```bash
# Run database migrations against your Neon PostgreSQL instance
.venv/bin/alembic upgrade head

# Seed catalog items (Blue Tokai specialty coffee collection)
.venv/bin/python -m src.db.seed
```

### 3. Running the Service
```bash
# Start Uvicorn ASGI server on port 8001
.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

Interactive OpenAPI / Swagger documentation is available at **`http://localhost:8001/docs`**.

---

## 🛠️ Tech Stack

* **Framework:** Python 3.10+ / FastAPI / Uvicorn
* **Database:** PostgreSQL (Neon) / SQLAlchemy 2.0 (Async) / asyncpg
* **Migrations:** Alembic
* **Validation:** Pydantic v2 / Pydantic Settings

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

### 1. Setting Up Python Virtual Environment (`venv`)

Ensure you have **Python 3.10+** installed on your system. It is strongly recommended to use an isolated virtual environment (`.venv`) to prevent dependency conflicts with other services.

```bash
# Navigate to the service root directory
cd product-catalog-service

# Create a dedicated virtual environment named .venv
python3 -m venv .venv
```

#### Activating the Virtual Environment

Activate the virtual environment depending on your operating system:

* **Linux / macOS (bash / zsh):**
  ```bash
  source .venv/bin/activate
  ```

* **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

* **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

> [!TIP]
> Verify that the active environment points to `.venv`:
> ```bash
> which python   # On Linux/macOS: should output .../product-catalog-service/.venv/bin/python
> which pip      # On Linux/macOS: should output .../product-catalog-service/.venv/bin/pip
> ```
> To exit the environment at any time, run `deactivate`.

---

### 2. Installing Dependencies

Once the virtual environment is activated:

#### A. Upgrade Build Tooling
Always ensure your package installer and build tools are up to date:
```bash
pip install --upgrade pip setuptools wheel
```

#### B. Install Service Dependencies
Install `product-catalog-service` in **editable mode** (`-e .`). This reads `pyproject.toml` and allows live code changes without needing to reinstall the package:

```bash
# Install core runtime dependencies (FastAPI, SQLAlchemy, Alembic, asyncpg, etc.)
pip install -e .
```

#### C. Optional: Install Development & Testing Tooling
If you plan to run automated test suites (`pytest`, `pytest-asyncio`) or code formatters/linters (`ruff`):

```bash
# Install with the [dev] optional dependencies defined in pyproject.toml
pip install -e ".[dev]"
```

---

### 3. Environment Configuration

Create a `.env` file in the root directory (or export the variables in your shell):

```bash
# Neon Serverless PostgreSQL connection string (asyncpg driver format)
# Note: postgres:// and postgresql:// are automatically normalized to postgresql+asyncpg://
DATABASE_URL="postgresql+asyncpg://<username>:<password>@<ep-identifier>.pooler.neon.tech/mycommerce-pim?ssl=require"

# Service Host & Port (defaults to 0.0.0.0:8001)
HOST="0.0.0.0"
PORT=8001
DEBUG=True
```

---

### 4. Database Migrations & Seeding (Alembic)

With the virtual environment active and `DATABASE_URL` configured:

```bash
# Apply schema migrations to the database
alembic upgrade head

# Populate the 24 curated Hiljhil Roasters catalog items (single origin estates, nano-lots & gear)
python -m src.db.seed
```

---

### 5. Running the Service

Start the FastAPI application using the Uvicorn ASGI server with live reloading enabled:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

* **Interactive OpenAPI / Swagger UI:** [`http://localhost:8001/docs`](http://localhost:8001/docs)
* **ReDoc Documentation:** [`http://localhost:8001/redoc`](http://localhost:8001/redoc)
* **Service Health Check:** [`http://localhost:8001/api/v1/health`](http://localhost:8001/api/v1/health)

---

## 🛠️ Tech Stack

* **Framework:** Python 3.10+ / FastAPI / Uvicorn
* **Database:** PostgreSQL (Neon) / SQLAlchemy 2.0 (Async) / asyncpg
* **Migrations:** Alembic
* **Validation:** Pydantic v2 / Pydantic Settings

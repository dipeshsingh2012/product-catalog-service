# Product Catalog Service (`product-catalog-service`)

> **E-Commerce Catalog API for Product Dimensions, Assets, & Space-Constrained Search**

`product-catalog-service` provides ground-truth dimensional specifications ($W \times H \times D$), cutout assets, clearance requirements, and dimensional search to support fitment verification and alternative product recommendations.

---

## 🎯 Responsibilities

1. **Dimensional Specifications:** Ground-truth physical dimensions in centimeters ($W \times H \times D$) and weights.
2. **Asset Management:** High-resolution transparent PNG cutouts (RGBA) and 3D bounding geometries.
3. **Clearance Rules:** Ventilation and operational clearance constraints (e.g. *"requires 10 cm top clearance for steam wand / bean hopper"*).
4. **Dimensional Alternative Search:** Queries for alternative products matching strict dimensional thresholds when an item exceeds kitchen space.

---

## 🏗️ API Endpoints

- `GET /api/v1/products/{id}` — Get single product dimensional specs and imagery.
- `GET /api/v1/products` — List products with category/price filters.
- `GET /api/v1/products/search/by-dimensions` — Search products constrained by `max_height_cm`, `max_width_cm`, `max_depth_cm`.

---

## 🚀 Tech Stack

- **Framework:** Python 3.10+ / FastAPI / Uvicorn
- **Database:** SQLite / SQLAlchemy / Pydantic v2

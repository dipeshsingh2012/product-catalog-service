import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.config import settings
from src.db.database import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("product_catalog")

tags_metadata = [
    {
        "name": "Products",
        "description": "Core product catalog operations, querying, creation, updating, and deletion with automated SKU synthesis.",
    },
    {
        "name": "Search & Fitment",
        "description": "Space-constrained dimensional search accounting for countertop clearance (width, height, depth).",
    },
    {
        "name": "Facets & Metadata",
        "description": "Catalog filter facets (categories, roast profiles, process methods, estates, price range) for storefronts.",
    },
    {
        "name": "Lifecycle",
        "description": "Product publishing and archiving state transitions.",
    },
    {
        "name": "Batch Operations",
        "description": "High-speed bulk imports and catalog synchronization.",
    },
    {
        "name": "Health",
        "description": "Liveness and service readiness monitoring.",
    },
]

api_description = """
# Hiljhil Roasters - Product Catalog Service ☕

High-performance e-commerce catalog API powered by **FastAPI**, **SQLAlchemy 2.0**, and **Neon Serverless PostgreSQL**.

### Key Features:
* **Specialty Coffee Craft & Terroir**: First-class attributes for single-origin estates, processing methods (washed, natural, carbonic maceration, honey anaerobic), roast profiles, tasting notes, and recommended brew methods.
* **Option B Hybrid Schema**: Relational indexing with PostgreSQL `JSONB` collections for packaging variants (250g, 500g, 1kg), flavor notes, and media galleries.
* **Automated SKU & Slug Engine**: Automatic synthesis of unique, collision-free SKUs (`HJ-[ESTATE]-[SIZE]`) and SEO slugs on product creation.
* **Dimensional Fitment Search**: Countertop clearance calculations (top steam clearance, side ventilation, rear airflow) for barista equipment and countertop appliances.
* **State-Aware Alembic Migrations**: Fully version-controlled schema rollouts integrated into CI/CD.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    # Clean up engine connections on shutdown
    if settings.DATABASE_URL:
        try:
            await engine.dispose()
        except Exception:
            pass


app = FastAPI(
    title="Hiljhil Roasters - Product Catalog API",
    summary="E-Commerce Catalog & Fitment API for Hiljhil Roasters specialty coffee and barista equipment.",
    description=api_description,
    version="0.1.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "operationsSorter": "alpha",
        "filter": True,
        "syntaxHighlight.theme": "monokai",
    },
    lifespan=lifespan,
)

# CORS middleware for PDP widgets and services
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    origin = request.headers.get("origin", "-")
    client_ip = request.client.host if request.client else "-"
    path = request.url.path
    query = request.url.query
    full_path = f"{path}?{query}" if query else path

    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"{request.method} {full_path} -> {response.status_code} "
            f"({duration_ms}ms) [origin: {origin}] [client: {client_ip}]"
        )
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"{request.method} {full_path} -> 500 ERROR ({duration_ms}ms) "
            f"[origin: {origin}] [client: {client_ip}]: {exc}",
            exc_info=True,
        )
        raise exc


app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Product Catalog Service is running",
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True)

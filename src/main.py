from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.config import settings
from src.db.database import engine

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
)

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

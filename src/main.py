from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.config import settings
from src.db.database import AsyncSessionLocal, Base, engine
from src.db.seed import seed_database


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
    title="Product Catalog Service",
    description="E-Commerce Catalog API for Product Dimensions, Cutouts, and Space-Constrained Search.",
    version="0.1.0",
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

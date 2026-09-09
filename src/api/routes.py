from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schemas.product import ProductCreate, ProductListResponse, ProductResponse
from src.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/v1", tags=["Products"])


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "product-catalog-service", "version": "0.1.0"}


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = Query(None, description="Filter by product category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    items, total = await service.list_products(category=category, brand=brand, limit=limit, offset=offset)
    return ProductListResponse(total=total, items=items)


@router.get("/products/search/by-dimensions", response_model=list[ProductResponse])
async def search_by_dimensions(
    max_height_cm: Optional[float] = Query(None, description="Maximum available vertical clearance in cm"),
    max_width_cm: Optional[float] = Query(None, description="Maximum available counter width in cm"),
    max_depth_cm: Optional[float] = Query(None, description="Maximum available counter depth in cm"),
    category: Optional[str] = Query(None, description="Category filter for alternatives"),
    exclude_id: Optional[str] = Query(None, description="Exclude target product ID from alternatives"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    results = await service.search_by_dimensions(
        max_height_cm=max_height_cm,
        max_width_cm=max_width_cm,
        max_depth_cm=max_depth_cm,
        category=category,
        exclude_id=exclude_id,
        limit=limit,
    )
    return results


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    existing = await service.get_by_id(data.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with ID '{data.id}' already exists",
        )
    return await service.create_product(data)


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate
from src.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/v1", tags=["Products"])


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "product-catalog-service", "version": "0.1.0"}


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    response: Response,
    category: Optional[str] = Query(None, description="Filter by product category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    status: Optional[str] = Query(None, description="Filter by status ('active', 'draft', 'archived')"),
    q: Optional[str] = Query(None, description="Search query by name, sku, or description"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _start: Optional[int] = Query(None, description="Refine pagination start offset"),
    _end: Optional[int] = Query(None, description="Refine pagination end offset"),
    db: AsyncSession = Depends(get_db),
):
    # Support Refine simple-rest pagination query params (_start & _end)
    if _start is not None and _end is not None:
        offset = _start
        limit = max(1, _end - _start)

    service = CatalogService(db)
    items, total = await service.list_products(
        category=category,
        brand=brand,
        status=status,
        q=q,
        limit=limit,
        offset=offset,
    )
    # Expose standard Refine / REST header
    response.headers["x-total-count"] = str(total)
    response.headers["Access-Control-Expose-Headers"] = "x-total-count"
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
    if data.id:
        existing = await service.get_by_id(data.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with ID '{data.id}' already exists",
            )
    return await service.create_product(data)


@router.put("/products/{product_id}", response_model=ProductResponse)
@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    product = await service.update_product(product_id, data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    hard_delete: bool = Query(False, description="Whether to permanently remove from database"),
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    success = await service.delete_product(product_id, hard_delete=hard_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    return None


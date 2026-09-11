from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schemas.product import (
    BulkProductCreateRequest,
    BulkProductResponse,
    CatalogFacetsResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from src.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/v1")


@router.get(
    "/health",
    tags=["Health"],
    summary="Health check & readiness status",
    description="Returns the running service status, service identifier, and version.",
)
async def health_check():
    return {"status": "ok", "service": "product-catalog-service", "version": "0.1.0"}


@router.get(
    "/products/facets",
    response_model=CatalogFacetsResponse,
    tags=["Facets & Metadata"],
    summary="Get catalog filter facets & price range",
    description="Returns distinct available categories, brands, roast profiles, processing methods, coffee estates, and catalog price bounds for UI filter bars.",
)
async def get_catalog_facets(db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    return await service.get_facets()


@router.get(
    "/products/search/by-dimensions",
    response_model=list[ProductResponse],
    tags=["Search & Fitment"],
    summary="Search products by dimensional countertop clearance",
    description="Finds coffee equipment, grinders, or accessories that fit within maximum available width, height (including lid/steam clearance), and depth constraints.",
)
async def search_by_dimensions(
    max_height_cm: Optional[float] = Query(None, description="Maximum available vertical clearance in cm (includes top clearance)"),
    max_width_cm: Optional[float] = Query(None, description="Maximum available counter width in cm (includes side clearances)"),
    max_depth_cm: Optional[float] = Query(None, description="Maximum available counter depth in cm (includes rear airflow clearance)"),
    category: Optional[str] = Query(None, description="Filter results by category"),
    exclude_id: Optional[str] = Query(None, description="Exclude target product ID from alternatives (e.g. current product on PDP)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum alternative matches to return"),
    db: AsyncSession = Depends(get_db),
):
    service = CatalogService(db)
    return await service.search_by_dimensions(
        max_height_cm=max_height_cm,
        max_width_cm=max_width_cm,
        max_depth_cm=max_depth_cm,
        category=category,
        exclude_id=exclude_id,
        limit=limit,
    )


@router.get(
    "/products/sku/{sku}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Get product by SKU",
    description="Retrieves a single product record using its unique Stock Keeping Unit (SKU).",
)
async def get_product_by_sku(sku: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    product = await service.get_by_sku(sku)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found",
        )
    return product


@router.get(
    "/products",
    response_model=ProductListResponse,
    tags=["Products"],
    summary="List & filter products",
    description="Lists catalog products with multi-attribute filtering (category, roast level, process method, estate), full-text search query, pagination, and Refine simple-rest support.",
)
async def list_products(
    response: Response,
    category: Optional[str] = Query(None, description="Filter by product category (e.g., 'single_estate', 'producer_series', 'blends', 'equipment')"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    status: Optional[str] = Query(None, description="Filter by status ('active', 'draft', 'archived')"),
    roast_level: Optional[str] = Query(None, description="Filter by roast profile ('light', 'medium', 'medium_dark', 'dark')"),
    process_method: Optional[str] = Query(None, description="Filter by coffee processing method ('washed', 'natural', 'anaerobic', 'carbonic_maceration')"),
    estate_name: Optional[str] = Query(None, description="Filter by origin estate name"),
    q: Optional[str] = Query(None, description="Full-text search query matching name, sku, estate, or description"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    _start: Optional[int] = Query(None, description="Refine pagination start offset"),
    _end: Optional[int] = Query(None, description="Refine pagination end offset"),
    db: AsyncSession = Depends(get_db),
):
    if _start is not None and _end is not None:
        offset = _start
        limit = max(1, _end - _start)

    service = CatalogService(db)
    items, total = await service.list_products(
        category=category,
        brand=brand,
        status=status,
        roast_level=roast_level,
        process_method=process_method,
        estate_name=estate_name,
        q=q,
        limit=limit,
        offset=offset,
    )
    response.headers["x-total-count"] = str(total)
    response.headers["Access-Control-Expose-Headers"] = "x-total-count"
    return ProductListResponse(total=total, items=items)


@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Get product by ID or Slug",
    description="Lookup a product using either its primary identifier (`prod_attikan_estate`) or SEO slug (`attikan-estate`).",
)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID or Slug '{product_id}' not found",
        )
    return product


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create new product",
    description="Creates a new catalog item. If `sku`, `slug`, or `id` are omitted, the API automatically synthesizes compliant, collision-free identifiers.",
)
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


@router.post(
    "/products/batch",
    response_model=BulkProductResponse,
    tags=["Batch Operations"],
    summary="Bulk import or upsert products",
    description="Batch process multiple products. Existing items matching `id` or `sku` are updated; new items are inserted with auto-generated SKUs.",
)
async def bulk_upsert_products(payload: BulkProductCreateRequest, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    inserted, updated = await service.bulk_upsert(payload.products)
    return BulkProductResponse(
        inserted=inserted,
        updated=updated,
        total=len(payload.products),
    )


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Update product (full)",
    description="Replaces product attributes for the specified ID.",
)
@router.patch(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"],
    summary="Update product (partial)",
    description="Applies partial updates to product attributes for the specified ID.",
)
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


@router.post(
    "/products/{product_id}/publish",
    response_model=ProductResponse,
    tags=["Lifecycle"],
    summary="Publish product",
    description="Transitions a product status to 'active', making it visible on the storefront and search queries.",
)
async def publish_product(product_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    product = await service.set_product_status(product_id, "active")
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    return product


@router.post(
    "/products/{product_id}/archive",
    response_model=ProductResponse,
    tags=["Lifecycle"],
    summary="Archive product",
    description="Transitions a product status to 'archived', hiding it from active storefront listings while preserving historical order data.",
)
async def archive_product(product_id: str, db: AsyncSession = Depends(get_db)):
    service = CatalogService(db)
    product = await service.set_product_status(product_id, "archived")
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    summary="Delete or soft-delete product",
    description="Soft-deletes (archives) the product by default, or permanently deletes it if `hard_delete=true`.",
)
async def delete_product(
    product_id: str,
    hard_delete: bool = Query(False, description="Whether to permanently remove from database (defaults to soft-delete archive)"),
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



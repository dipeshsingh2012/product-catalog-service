from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Product
from src.schemas.product import ProductCreate


class CatalogService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalars().first()

    async def list_products(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Product], int]:
        stmt = select(Product)
        if category:
            stmt = stmt.where(Product.category == category)
        if brand:
            stmt = stmt.where(Product.brand == brand)

        count_stmt = select(Product.id)
        if category:
            count_stmt = count_stmt.where(Product.category == category)
        if brand:
            count_stmt = count_stmt.where(Product.brand == brand)

        count_res = await self.session.execute(count_stmt)
        total = len(count_res.scalars().all())

        stmt = stmt.offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all()), total

    async def search_by_dimensions(
        self,
        max_height_cm: Optional[float] = None,
        max_width_cm: Optional[float] = None,
        max_depth_cm: Optional[float] = None,
        category: Optional[str] = None,
        exclude_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[Product]:
        stmt = select(Product)

        if exclude_id:
            stmt = stmt.where(Product.id != exclude_id)
        if category:
            stmt = stmt.where(Product.category == category)

        # Condition: height_cm + top_clearance_cm <= max_height_cm
        if max_height_cm is not None:
            stmt = stmt.where((Product.height_cm + Product.top_clearance_cm) <= max_height_cm)
        if max_width_cm is not None:
            stmt = stmt.where((Product.width_cm + (2 * Product.side_clearance_cm)) <= max_width_cm)
        if max_depth_cm is not None:
            stmt = stmt.where((Product.depth_cm + Product.rear_clearance_cm) <= max_depth_cm)

        stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_product(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product


import re
from typing import Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Product
from src.schemas.product import ProductCreate, ProductUpdate


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
        status: Optional[str] = None,
        q: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Product], int]:
        stmt = select(Product)

        if status:
            stmt = stmt.where(Product.status == status)
        if category:
            stmt = stmt.where(Product.category == category)
        if brand:
            stmt = stmt.where(Product.brand == brand)
        if q:
            search_pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.brand.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                )
            )

        count_stmt = select(Product.id)
        if status:
            count_stmt = count_stmt.where(Product.status == status)
        if category:
            count_stmt = count_stmt.where(Product.category == category)
        if brand:
            count_stmt = count_stmt.where(Product.brand == brand)
        if q:
            search_pattern = f"%{q}%"
            count_stmt = count_stmt.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.brand.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                )
            )

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
        dump = data.model_dump()
        if not dump.get("id"):
            slug = re.sub(r"[^a-z0-9]+", "_", data.name.lower()).strip("_")
            dump["id"] = f"prod_{slug}"

        product = Product(**dump)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update_product(self, product_id: str, data: ProductUpdate) -> Optional[Product]:
        product = await self.get_by_id(product_id)
        if not product:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(product, key, value)

        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete_product(self, product_id: str, hard_delete: bool = False) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False

        if hard_delete:
            await self.session.delete(product)
        else:
            product.status = "archived"
        await self.session.commit()
        return True


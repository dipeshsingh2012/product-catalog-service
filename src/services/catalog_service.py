import json
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
            select(Product).where(
                or_(
                    Product.id == product_id,
                    Product.slug == product_id,
                )
            )
        )
        return result.scalars().first()

    async def list_products(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        status: Optional[str] = None,
        roast_level: Optional[str] = None,
        process_method: Optional[str] = None,
        estate_name: Optional[str] = None,
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
        if roast_level:
            stmt = stmt.where(Product.roast_level == roast_level)
        if process_method:
            stmt = stmt.where(Product.process_method == process_method)
        if estate_name:
            stmt = stmt.where(Product.estate_name.ilike(f"%{estate_name}%"))

        if q:
            search_pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.brand.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.estate_name.ilike(search_pattern),
                    Product.region.ilike(search_pattern),
                    Product.varietal.ilike(search_pattern),
                )
            )

        count_stmt = select(Product.id)
        if status:
            count_stmt = count_stmt.where(Product.status == status)
        if category:
            count_stmt = count_stmt.where(Product.category == category)
        if brand:
            count_stmt = count_stmt.where(Product.brand == brand)
        if roast_level:
            count_stmt = count_stmt.where(Product.roast_level == roast_level)
        if process_method:
            count_stmt = count_stmt.where(Product.process_method == process_method)
        if estate_name:
            count_stmt = count_stmt.where(Product.estate_name.ilike(f"%{estate_name}%"))

        if q:
            search_pattern = f"%{q}%"
            count_stmt = count_stmt.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.brand.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.estate_name.ilike(search_pattern),
                    Product.region.ilike(search_pattern),
                    Product.varietal.ilike(search_pattern),
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

        if max_height_cm is not None:
            stmt = stmt.where((Product.height_cm + Product.top_clearance_cm) <= max_height_cm)
        if max_width_cm is not None:
            stmt = stmt.where((Product.width_cm + (2 * Product.side_clearance_cm)) <= max_width_cm)
        if max_depth_cm is not None:
            stmt = stmt.where((Product.depth_cm + Product.rear_clearance_cm) <= max_depth_cm)

        stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def _generate_unique_sku(
        self,
        name: str,
        brand: Optional[str] = "Hiljhil Roasters",
        estate_name: Optional[str] = None,
        weight_kg: Optional[float] = 0.25,
    ) -> str:
        brand_clean = (brand or "Hiljhil Roasters").strip()
        if "hiljhil" in brand_clean.lower():
            prefix = "HJ"
        else:
            words = re.findall(r"[A-Za-z0-9]+", brand_clean)
            prefix = "".join(w[0] for w in words).upper()[:4] if words else "GEN"

        if estate_name and estate_name.strip():
            tokens = [t.upper() for t in re.findall(r"[A-Za-z0-9]+", estate_name) if t.lower() != "estate"]
            if not tokens:
                tokens = [t.upper() for t in re.findall(r"[A-Za-z0-9]+", estate_name)]
            descriptor = "-".join(tokens[:2])
        else:
            skip_words = {"coffee", "beans", "pouch"}
            tokens = [t.upper() for t in re.findall(r"[A-Za-z0-9]+", name) if t.lower() not in skip_words]
            if not tokens:
                tokens = [t.upper() for t in re.findall(r"[A-Za-z0-9]+", name)]
            descriptor = "-".join(tokens[:2])

        if weight_kg is not None and weight_kg > 0:
            if weight_kg >= 1.0:
                size_str = f"{int(weight_kg) if isinstance(weight_kg, int) or weight_kg.is_integer() else weight_kg}KG"
            else:
                size_str = str(int(weight_kg * 1000))
        else:
            size_str = "250"

        base_sku = f"{prefix}-{descriptor}-{size_str}"

        candidate_sku = base_sku
        counter = 1
        while True:
            existing = await self.get_by_sku(candidate_sku)
            if not existing:
                return candidate_sku
            counter += 1
            candidate_sku = f"{base_sku}-{counter}"

    async def create_product(self, data: ProductCreate) -> Product:
        dump = data.model_dump()

        # Generate slug if missing
        if not dump.get("slug"):
            dump["slug"] = re.sub(r"[^a-z0-9]+", "-", data.name.lower()).strip("-")

        # Generate id if missing
        if not dump.get("id"):
            clean_slug = dump["slug"].replace("-", "_")
            dump["id"] = f"prod_{clean_slug}"

        # Generate SKU if missing
        if not dump.get("sku"):
            dump["sku"] = await self._generate_unique_sku(
                name=data.name,
                brand=dump.get("brand"),
                estate_name=dump.get("estate_name"),
                weight_kg=dump.get("weight_kg"),
            )

        # Auto-generate variant SKUs if missing in variants array
        if dump.get("variants") and isinstance(dump["variants"], list):
            brand_val = dump.get("brand") or "Hiljhil Roasters"
            pfx = "HJ" if "hiljhil" in brand_val.lower() else "".join(re.findall(r"[A-Za-z0-9]+", brand_val)[:2]).upper()[:4]
            desc = dump["sku"].split("-")[1] if len(dump["sku"].split("-")) > 1 else "ITEM"
            updated_variants = []
            for v in dump["variants"]:
                if isinstance(v, dict):
                    v_dict = dict(v)
                    if not v_dict.get("sku"):
                        size_raw = v_dict.get("size", "")
                        clean_sz = re.sub(r"[^A-Za-z0-9]+", "", size_raw).upper() or "VAR"
                        v_dict["sku"] = f"{pfx}-{desc}-{clean_sz}"
                    updated_variants.append(v_dict)
                else:
                    updated_variants.append(v)
            dump["variants"] = updated_variants

        # Sync taste_notes list into taste_notes_json if missing
        if dump.get("taste_notes") and not dump.get("taste_notes_json"):
            dump["taste_notes_json"] = json.dumps(dump["taste_notes"])

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

        if "taste_notes" in update_dict and "taste_notes_json" not in update_dict:
            update_dict["taste_notes_json"] = json.dumps(update_dict["taste_notes"])

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

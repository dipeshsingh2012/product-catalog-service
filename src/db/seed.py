from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models import Product

SEED_PRODUCTS = [
    {
        "id": "prod_breville_barista_touch",
        "name": "Barista Touch Espresso Machine",
        "brand": "Breville",
        "sku": "BES880BSS",
        "category": "espresso_machine",
        "price": 999.95,
        "width_cm": 32.2,
        "height_cm": 40.7,
        "depth_cm": 32.2,
        "weight_kg": 10.3,
        "top_clearance_cm": 12.0,  # For bean hopper refilling
        "side_clearance_cm": 5.0,
        "rear_clearance_cm": 5.0,
        "image_url": "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=600&auto=format&fit=crop&q=80",
        "cutout_url": "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=600&auto=format&fit=crop&q=80",
        "description": "Automated touchscreen espresso machine with integrated precision grinder and automated microfoam milk texturing.",
        "specs_json": '{"voltage": "120V", "water_tank_l": 2.0, "bean_hopper_g": 250}',
    },
    {
        "id": "prod_vitamix_5200",
        "name": "5200 Professional Blender",
        "brand": "Vitamix",
        "sku": "VM0103",
        "category": "blender",
        "price": 499.95,
        "width_cm": 22.2,
        "height_cm": 52.0,  # Very tall - often clashes with 45cm under-cabinet space
        "depth_cm": 18.5,
        "weight_kg": 4.8,
        "top_clearance_cm": 6.0,
        "side_clearance_cm": 3.0,
        "rear_clearance_cm": 3.0,
        "image_url": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&auto=format&fit=crop&q=80",
        "cutout_url": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=600&auto=format&fit=crop&q=80",
        "description": "Classic 64-ounce container blender engineered for high performance smoothies, soups, and purees.",
        "specs_json": '{"container_oz": 64, "power_hp": 2.0}',
    },
    {
        "id": "prod_delonghi_dedica",
        "name": "Dedica Deluxe Slim Espresso Machine",
        "brand": "De'Longhi",
        "sku": "EC680M",
        "category": "espresso_machine",
        "price": 299.95,
        "width_cm": 14.9,  # Ultra-compact slim profile
        "height_cm": 30.5,
        "depth_cm": 33.0,
        "weight_kg": 4.2,
        "top_clearance_cm": 5.0,
        "side_clearance_cm": 3.0,
        "rear_clearance_cm": 4.0,
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
        "cutout_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
        "description": "Ultra-slim 6-inch wide manual espresso machine engineered for constrained countertop spaces.",
        "specs_json": '{"pressure_bar": 15, "water_tank_l": 1.0}',
    },
    {
        "id": "prod_breville_bambino",
        "name": "Bambino Plus Compact Espresso Machine",
        "brand": "Breville",
        "sku": "BES500BSS",
        "category": "espresso_machine",
        "price": 499.95,
        "width_cm": 19.5,
        "height_cm": 31.0,
        "depth_cm": 32.0,
        "weight_kg": 4.95,
        "top_clearance_cm": 5.0,
        "side_clearance_cm": 3.0,
        "rear_clearance_cm": 4.0,
        "image_url": "https://images.unsplash.com/photo-1509785307050-d4066910ec1e?w=600&auto=format&fit=crop&q=80",
        "cutout_url": "https://images.unsplash.com/photo-1509785307050-d4066910ec1e?w=600&auto=format&fit=crop&q=80",
        "description": "Compact espresso machine delivering barista-quality coffee with 3-second thermo-jet heatup.",
        "specs_json": '{"pressure_bar": 15, "heating_sec": 3}',
    },
    {
        "id": "prod_kitchenaid_artisan",
        "name": "Artisan Series 5-Quart Stand Mixer",
        "brand": "KitchenAid",
        "sku": "KSM150PSER",
        "category": "stand_mixer",
        "price": 449.99,
        "width_cm": 22.2,
        "height_cm": 35.6,
        "depth_cm": 36.2,
        "weight_kg": 11.8,
        "top_clearance_cm": 14.0,  # Requires head-tilt clearance
        "side_clearance_cm": 5.0,
        "rear_clearance_cm": 5.0,
        "image_url": "https://images.unsplash.com/photo-1594385208974-2e75f8d7bb48?w=600&auto=format&fit=crop&q=80",
        "cutout_url": "https://images.unsplash.com/photo-1594385208974-2e75f8d7bb48?w=600&auto=format&fit=crop&q=80",
        "description": "Tilt-head stand mixer for recipes from chocolate chip cookies to shredded chicken.",
        "specs_json": '{"bowl_qt": 5.0, "speeds": 10}',
    },
    {
        "id": "prod_ninja_airfryer_xl",
        "name": "Foodi XL 6-in-1 10-Qt Air Fryer",
        "brand": "Ninja",
        "sku": "DZ401",
        "category": "air_fryer",
        "price": 229.99,
        "width_cm": 43.4,
        "height_cm": 32.5,
        "depth_cm": 37.1,
        "weight_kg": 8.9,
        "top_clearance_cm": 12.0,  # Hot air ventilation
        "side_clearance_cm": 8.0,
        "rear_clearance_cm": 10.0,
        "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80",
        "cutout_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80",
        "description": "DualZone Technology 2-basket air fryer to cook 2 foods, 2 ways that finish at the same time.",
        "specs_json": '{"baskets": 2, "capacity_qt": 10.0}',
    },
]


async def seed_database(session: AsyncSession):
    result = await session.execute(select(Product))
    existing = result.scalars().first()
    if existing is not None:
        return  # already seeded

    for item in SEED_PRODUCTS:
        prod = Product(**item)
        session.add(prod)
    await session.commit()


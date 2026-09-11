from sqlalchemy import Boolean, Column, Float, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from src.db.database import Base

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class Product(Base):
    __tablename__ = "products"

    # Core Identifiers
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    brand = Column(String, nullable=False, default="Hiljhil Roasters", index=True)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)

    # Status & Merchandising
    status = Column(String, default="active", index=True)  # active, draft, archived
    in_stock = Column(Boolean, default=True)
    badge = Column(String, nullable=True)  # e.g., 'BESTSELLER', 'LIMITED RELEASE', 'NEW HARVEST'
    rating = Column(Float, default=5.0)
    review_count = Column(Integer, default=0)
    tax_category = Column(String, default="coffee_beans")  # 5% GST

    # Physical Dimensions (in centimeters, reference pouch 250g)
    width_cm = Column(Float, nullable=False, default=12.0)
    height_cm = Column(Float, nullable=False, default=20.0)
    depth_cm = Column(Float, nullable=False, default=6.0)
    weight_kg = Column(Float, nullable=True, default=0.25)

    # Operational & Ventilation Clearances (in centimeters)
    top_clearance_cm = Column(Float, default=0.0)
    side_clearance_cm = Column(Float, default=0.0)
    rear_clearance_cm = Column(Float, default=0.0)

    # Specialty Coffee Terroir & Craft
    roast_level = Column(String, nullable=True, index=True)  # light, medium, medium_dark, dark
    process_method = Column(String, nullable=True, index=True)  # washed, natural, anaerobic, etc.
    estate_name = Column(String, nullable=True, index=True)
    region = Column(String, nullable=True)  # e.g. Biligiriranga Hills, Karnataka
    elevation_m = Column(Integer, nullable=True)
    varietal = Column(String, nullable=True)  # e.g. Selection 9, S795
    resting_period_days = Column(Integer, nullable=True)  # Recommended degassing / resting period
    acidity = Column(String, nullable=True)  # low, medium, medium_high
    bitterness = Column(String, nullable=True)  # low, medium, medium_high
    body = Column(String, nullable=True)  # Medium-High, Silky, Velvety
    best_enjoyed = Column(String, nullable=True)  # black, with_milk, both

    # Media Assets & Descriptions
    image_url = Column(String, nullable=True)  # Primary hero front-pack image
    cutout_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Rich JSONB Collections
    taste_notes = Column(JSON_TYPE, nullable=True)  # ["Dark Chocolate", "Nutty", "Almond"]
    recommended_brew_methods = Column(JSON_TYPE, nullable=True)  # ["espresso", "pour_over", "aeropress"]
    variants = Column(JSON_TYPE, nullable=True)  # Pack sizes: [{"size": "250g", "price": 700.0, ...}]
    images = Column(JSON_TYPE, nullable=True)  # Gallery: [{"position": 1, "src": "...", ...}]

    # Legacy / String compatibility
    taste_notes_json = Column(Text, nullable=True)
    specs_json = Column(Text, nullable=True)

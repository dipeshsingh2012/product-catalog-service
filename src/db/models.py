from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from src.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)

    # Status & Merchandising
    status = Column(String, default="active", index=True)  # active, draft, archived
    in_stock = Column(Boolean, default=True)
    badge = Column(String, nullable=True)  # e.g., 'EXCLUSIVE HARVEST', 'BESTSELLER', 'NEW'
    rating = Column(Float, default=5.0)
    review_count = Column(Integer, default=0)
    tax_category = Column(String, default="coffee_beans")  # coffee_beans, equipment, accessories, exempt

    # Physical Dimensions (in centimeters)
    width_cm = Column(Float, nullable=False, default=0.0)
    height_cm = Column(Float, nullable=False, default=0.0)
    depth_cm = Column(Float, nullable=False, default=0.0)
    weight_kg = Column(Float, nullable=True)

    # Operational & Ventilation Clearances (in centimeters)
    top_clearance_cm = Column(Float, default=0.0)
    side_clearance_cm = Column(Float, default=0.0)
    rear_clearance_cm = Column(Float, default=0.0)

    # Assets
    image_url = Column(String, nullable=True)
    cutout_url = Column(String, nullable=True)

    # Metadata, description & specialized attributes
    description = Column(Text, nullable=True)
    taste_notes_json = Column(Text, nullable=True)  # JSON array: ["Ripe Banana", "Red Plum"]
    specs_json = Column(Text, nullable=True)  # JSON object with key-value specs


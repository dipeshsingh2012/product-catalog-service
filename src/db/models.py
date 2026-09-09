from sqlalchemy import Column, Float, Integer, String, Text
from src.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)

    # Physical Dimensions (in centimeters)
    width_cm = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    depth_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=True)

    # Operational & Ventilation Clearances (in centimeters)
    top_clearance_cm = Column(Float, default=0.0)
    side_clearance_cm = Column(Float, default=0.0)
    rear_clearance_cm = Column(Float, default=0.0)

    # Assets
    image_url = Column(String, nullable=True)
    cutout_url = Column(String, nullable=True)

    # Metadata & description
    description = Column(Text, nullable=True)
    specs_json = Column(Text, nullable=True)


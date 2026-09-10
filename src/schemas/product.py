from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ClearanceRules(BaseModel):
    top_clearance_cm: float = Field(0.0, description="Required vertical clearance for lids/steam/ventilation")
    side_clearance_cm: float = Field(0.0, description="Required side clearance for ventilation/access")
    rear_clearance_cm: float = Field(0.0, description="Required rear clearance for airflow/cables")


class PhysicalDimensions(BaseModel):
    width_cm: float = Field(..., description="Product physical width in cm")
    height_cm: float = Field(..., description="Product physical height in cm")
    depth_cm: float = Field(..., description="Product physical depth in cm")
    weight_kg: Optional[float] = Field(None, description="Product weight in kg")


class ProductBase(BaseModel):
    name: str
    brand: str
    sku: str
    category: str
    price: float
    compare_at_price: Optional[float] = None
    status: str = Field("active", description="'active', 'draft', or 'archived'")
    in_stock: bool = Field(True, description="Whether the product is available to purchase")
    badge: Optional[str] = None
    rating: float = 5.0
    review_count: int = 0
    tax_category: str = Field("coffee_beans", description="Tax classification code")
    width_cm: float = 0.0
    height_cm: float = 0.0
    depth_cm: float = 0.0
    weight_kg: Optional[float] = None
    top_clearance_cm: float = 0.0
    side_clearance_cm: float = 0.0
    rear_clearance_cm: float = 0.0
    image_url: Optional[str] = None
    cutout_url: Optional[str] = None
    description: Optional[str] = None
    taste_notes_json: Optional[str] = None
    specs_json: Optional[str] = None


class ProductCreate(ProductBase):
    id: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    status: Optional[str] = None
    in_stock: Optional[bool] = None
    badge: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    tax_category: Optional[str] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    depth_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    top_clearance_cm: Optional[float] = None
    side_clearance_cm: Optional[float] = None
    rear_clearance_cm: Optional[float] = None
    image_url: Optional[str] = None
    cutout_url: Optional[str] = None
    description: Optional[str] = None
    taste_notes_json: Optional[str] = None
    specs_json: Optional[str] = None


class ProductResponse(ProductBase):
    id: str

    @property
    def total_required_height_cm(self) -> float:
        return self.height_cm + self.top_clearance_cm

    @property
    def total_required_width_cm(self) -> float:
        return self.width_cm + (2 * self.side_clearance_cm)

    @property
    def total_required_depth_cm(self) -> float:
        return self.depth_cm + self.rear_clearance_cm

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    total: int
    items: list[ProductResponse]


class DimensionSearchQuery(BaseModel):
    max_height_cm: Optional[float] = None
    max_width_cm: Optional[float] = None
    max_depth_cm: Optional[float] = None
    category: Optional[str] = None
    limit: int = 10


from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import ProductStatus


class ProductCreate(BaseModel):
    photo_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    size: str = Field(min_length=1, max_length=50)
    material: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    status: ProductStatus = ProductStatus.AVAILABLE


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    size: str | None = Field(default=None, min_length=1, max_length=50)
    material: str | None = Field(default=None, min_length=1, max_length=100)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    status: ProductStatus | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_id: int
    name: str
    size: str
    material: str
    price: Decimal
    stock: int
    status: ProductStatus
    created_at: datetime
    updated_at: datetime
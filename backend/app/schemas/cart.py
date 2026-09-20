from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.product import ProductStatus


class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_id: int
    name: str
    size: str
    material: str
    price: Decimal
    stock: int
    status: ProductStatus


class CartItemResponse(BaseModel):
    id: int
    product: CartProductResponse
    quantity: int
    subtotal: Decimal


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total_amount: Decimal
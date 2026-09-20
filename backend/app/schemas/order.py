from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class PhotographerOrderResponse(BaseModel):
    id: int
    status: OrderStatus
    related_total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]
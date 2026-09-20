from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import (
    get_db_session,
    require_administrator,
    require_customer,
    require_photographer,
)
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.photo import PhotoStatus
from app.models.product import Product, ProductStatus
from app.models.user import User
from app.schemas.order import (
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdate,
    PhotographerOrderResponse,
)


router = APIRouter(prefix="/orders", tags=["Orders"])

ALLOWED_STATUS_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.COMPLETED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


def get_customer_cart(db: Session, customer: User) -> Cart:
    query = (
        select(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.product).joinedload(Product.photo))
        .where(Cart.user_id == customer.id)
    )
    cart = db.execute(query).unique().scalar_one_or_none()
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


def get_customer_order(db: Session, customer: User, order_id: int) -> Order:
    query = (
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .where(Order.id == order_id, Order.customer_id == customer.id)
    )
    order = db.execute(query).unique().scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def get_order_or_404(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def build_item_response(item: OrderItem) -> OrderItemResponse:
    subtotal = item.unit_price * item.quantity
    return OrderItemResponse(
        product_id=item.product_id,
        product_name=item.product.name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=subtotal,
    )


def build_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[build_item_response(item) for item in order.items],
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> OrderResponse:
    cart = get_customer_cart(db, current_user)
    if not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot place an order with an empty cart")

    try:
        validated_items: list[tuple[CartItem, Product]] = []
        total = Decimal("0.00")
        for cart_item in cart.items:
            product = db.scalar(
                select(Product)
                .options(joinedload(Product.photo))
                .where(Product.id == cart_item.product_id)
                .with_for_update()
            )
            if product is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart product not found")
            if product.status != ProductStatus.AVAILABLE:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A cart product is no longer available")
            if product.photo.status != PhotoStatus.PUBLISHED:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A cart product photo is no longer published")
            if cart_item.quantity > product.stock:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart quantity exceeds available stock")
            validated_items.append((cart_item, product))
            total += product.price * cart_item.quantity

        order = Order(customer_id=current_user.id, status=OrderStatus.PENDING, total_amount=total)
        db.add(order)
        db.flush()
        for cart_item, product in validated_items:
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    unit_price=product.price,
                )
            )
            product.stock -= cart_item.quantity
            db.delete(cart_item)
        db.commit()
        db.refresh(order)
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order could not be created") from None

    order = get_customer_order(db, current_user, order.id)
    return build_order_response(order)


@router.get("", response_model=list[OrderResponse])
def list_customer_orders(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> list[OrderResponse]:
    orders = db.scalars(
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .where(Order.customer_id == current_user.id)
        .order_by(Order.id)
    ).unique().all()
    return [build_order_response(order) for order in orders]


@router.get("/photographer", response_model=list[PhotographerOrderResponse])
def list_photographer_orders(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> list[PhotographerOrderResponse]:
    profile = current_user.photographer_profile
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photographer profile not found")
    product_ids = select(Product.id).where(Product.photo.has(photographer_id=profile.id))
    orders = db.scalars(
        select(Order)
        .join(OrderItem)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .where(OrderItem.product_id.in_(product_ids))
        .distinct()
        .order_by(Order.id)
    ).unique().all()
    responses = []
    for order in orders:
        related_items = [item for item in order.items if item.product.photo.photographer_id == profile.id]
        related_total = sum((item.unit_price * item.quantity for item in related_items), Decimal("0.00"))
        responses.append(
            PhotographerOrderResponse(
                id=order.id,
                status=order.status,
                related_total=related_total,
                created_at=order.created_at,
                items=[build_item_response(item) for item in related_items],
            )
        )
    return responses


@router.get("/{order_id}", response_model=OrderResponse)
def get_customer_order_details(
    order_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> OrderResponse:
    return build_order_response(get_customer_order(db, current_user, order_id))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> OrderResponse:
    order = get_customer_order(db, current_user, order_id)
    if OrderStatus.CANCELLED not in ALLOWED_STATUS_TRANSITIONS.get(order.status, set()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be cancelled in its current status")
    for item in order.items:
        item.product.stock += item.quantity
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return build_order_response(get_customer_order(db, current_user, order.id))


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db_session),
    _: User = Depends(require_administrator),
) -> OrderResponse:
    order = get_order_or_404(db, order_id)
    if payload.status not in ALLOWED_STATUS_TRANSITIONS.get(order.status, set()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status transition")
    order.status = payload.status
    db.commit()
    order = db.execute(
        select(Order).options(joinedload(Order.items).joinedload(OrderItem.product)).where(Order.id == order.id)
    ).unique().scalar_one()
    return build_order_response(order)
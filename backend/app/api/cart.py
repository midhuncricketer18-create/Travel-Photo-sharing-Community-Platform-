from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_db_session, require_customer
from app.models.cart import Cart, CartItem
from app.models.photo import PhotoStatus
from app.models.product import Product, ProductStatus
from app.models.user import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartProductResponse,
    CartResponse,
)


router = APIRouter(prefix="/cart", tags=["Cart"])


def get_or_create_cart(db: Session, user: User) -> Cart:
    query = (
        select(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.product))
        .where(Cart.user_id == user.id)
    )
    cart = db.execute(query).unique().scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def get_cart_item(db: Session, user: User, item_id: int) -> CartItem:
    item = db.scalar(
        select(CartItem)
        .join(Cart)
        .options(joinedload(CartItem.product))
        .where(Cart.user_id == user.id, CartItem.id == item_id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    return item


def get_purchasable_product(db: Session, product_id: int) -> Product:
    product = db.scalar(
        select(Product)
        .options(joinedload(Product.photo))
        .where(Product.id == product_id)
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.status != ProductStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not available")
    if product.photo.status != PhotoStatus.PUBLISHED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product photo is not published")
    return product


def build_cart_response(cart: Cart) -> CartResponse:
    items = []
    total = Decimal("0.00")
    for item in sorted(cart.items, key=lambda cart_item: cart_item.id):
        subtotal = item.product.price * item.quantity
        total += subtotal
        items.append(
            CartItemResponse(
                id=item.id,
                product=CartProductResponse.model_validate(item.product),
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )
    return CartResponse(id=cart.id, user_id=cart.user_id, items=items, total_amount=total)


@router.get("", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> CartResponse:
    return build_cart_response(get_or_create_cart(db, current_user))


@router.get("/items", response_model=list[CartItemResponse])
def get_cart_items(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> list[CartItemResponse]:
    return get_cart(db, current_user).items


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: CartItemCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> CartResponse:
    cart = get_or_create_cart(db, current_user)
    product = get_purchasable_product(db, payload.product_id)
    existing_item = db.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id)
    )
    requested_quantity = payload.quantity + (existing_item.quantity if existing_item else 0)
    if requested_quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock")

    if existing_item:
        existing_item.quantity = requested_quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=requested_quantity))
    db.commit()
    return build_cart_response(get_or_create_cart(db, current_user))


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> CartResponse:
    item = get_cart_item(db, current_user, item_id)
    product = get_purchasable_product(db, item.product_id)
    if payload.quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock")
    item.quantity = payload.quantity
    db.commit()
    return build_cart_response(get_or_create_cart(db, current_user))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_customer),
) -> None:
    item = get_cart_item(db, current_user, item_id)
    db.delete(item)
    db.commit()
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.orders import build_order_response
from app.core.dependencies import get_db_session, require_administrator
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.photo import Photo
from app.models.photographer import Photographer
from app.models.product import Product
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.order import OrderResponse
from app.schemas.photo import PhotoResponse
from app.schemas.photographer import PhotographerResponse
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_administrator),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)).all())


@router.get("/photographers", response_model=list[PhotographerResponse])
def list_photographers(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_administrator),
) -> list[Photographer]:
    return list(db.scalars(select(Photographer).order_by(Photographer.id)).all())


@router.get("/photos", response_model=list[PhotoResponse])
def list_photos(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_administrator),
) -> list[Photo]:
    return list(db.scalars(select(Photo).order_by(Photo.id)).all())


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_administrator),
) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.id)).all())


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db_session),
    _: User = Depends(require_administrator),
) -> list[OrderResponse]:
    orders = db.scalars(
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .order_by(Order.id)
    ).unique().all()
    return [build_order_response(order) for order in orders]

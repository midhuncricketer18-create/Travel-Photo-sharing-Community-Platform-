from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_db_session, require_photographer
from app.models.photo import Photo, PhotoStatus
from app.models.photographer import Photographer
from app.models.product import Product, ProductStatus
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(prefix="/products", tags=["Products"])


def get_profile(db: Session, user: User) -> Photographer:
    profile = db.scalar(select(Photographer).where(Photographer.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photographer profile not found")
    return profile


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def ensure_product_owner(product: Product, profile: Photographer) -> None:
    if product.photo.photographer_id != profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this product")


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Product:
    profile = get_profile(db, current_user)
    photo = db.get(Photo, payload.photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if photo.photographer_id != profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this photo")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/mine", response_model=list[ProductResponse])
def list_my_products(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> list[Product]:
    profile = get_profile(db, current_user)
    query = select(Product).join(Photo).where(Photo.photographer_id == profile.id).order_by(Product.id)
    return list(db.scalars(query).all())


@router.get("", response_model=list[ProductResponse])
def list_available_products(
    db: Session = Depends(get_db_session),
) -> list[Product]:
    query = (
        select(Product)
        .join(Photo)
        .where(Product.status == ProductStatus.AVAILABLE, Photo.status == PhotoStatus.PUBLISHED)
        .order_by(Product.id)
    )
    return list(db.scalars(query).all())


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db_session),
) -> Product:
    product = get_product_or_404(db, product_id)
    if product.status != ProductStatus.AVAILABLE or product.photo.status != PhotoStatus.PUBLISHED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Product:
    profile = get_profile(db, current_user)
    product = get_product_or_404(db, product_id)
    ensure_product_owner(product, profile)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> None:
    profile = get_profile(db, current_user)
    product = get_product_or_404(db, product_id)
    ensure_product_owner(product, profile)
    db.delete(product)
    db.commit()
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_db_session, require_photographer
from app.models.photo import Photo, PhotoStatus
from app.models.photographer import Photographer
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoResponse, PhotoUpdate


router = APIRouter(prefix="/photos", tags=["Photos"])


def get_photographer_profile(db: Session, user: User) -> Photographer:
    profile = db.scalar(select(Photographer).where(Photographer.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photographer profile not found")
    return profile


def get_photo_or_404(db: Session, photo_id: int) -> Photo:
    photo = db.get(Photo, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


def ensure_photo_owner(photo: Photo, profile: Photographer) -> None:
    if photo.photographer_id != profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this photo")


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def create_photo(
    payload: PhotoCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Photo:
    profile = get_photographer_profile(db, current_user)
    photo = Photo(photographer_id=profile.id, **payload.model_dump())
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/mine", response_model=list[PhotoResponse])
def list_my_photos(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> list[Photo]:
    profile = get_photographer_profile(db, current_user)
    return list(db.scalars(select(Photo).where(Photo.photographer_id == profile.id).order_by(Photo.id)).all())


@router.get("", response_model=list[PhotoResponse])
def list_published_photos(
    db: Session = Depends(get_db_session),
) -> list[Photo]:
    return list(db.scalars(select(Photo).where(Photo.status == PhotoStatus.PUBLISHED).order_by(Photo.id)).all())


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(
    photo_id: int,
    db: Session = Depends(get_db_session),
) -> Photo:
    photo = get_photo_or_404(db, photo_id)
    if photo.status != PhotoStatus.PUBLISHED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


@router.put("/{photo_id}", response_model=PhotoResponse)
def update_photo(
    photo_id: int,
    payload: PhotoUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Photo:
    profile = get_photographer_profile(db, current_user)
    photo = get_photo_or_404(db, photo_id)
    ensure_photo_owner(photo, profile)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(photo, field, value)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> None:
    profile = get_photographer_profile(db, current_user)
    photo = get_photo_or_404(db, photo_id)
    ensure_photo_owner(photo, profile)
    db.delete(photo)
    db.commit()
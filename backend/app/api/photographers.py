from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_db_session, require_photographer
from app.models.photographer import Photographer
from app.models.user import User
from app.schemas.photographer import (
    PhotographerCreate,
    PhotographerResponse,
    PhotographerUpdate,
)


router = APIRouter(prefix="/photographers", tags=["Photographers"])


def get_owned_profile(db: Session, user: User) -> Photographer:
    profile = db.scalar(select(Photographer).where(Photographer.user_id == user.id))
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photographer profile not found")
    return profile


@router.post("/profile", response_model=PhotographerResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: PhotographerCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Photographer:
    existing = db.scalar(select(Photographer).where(Photographer.user_id == current_user.id))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Photographer profile already exists")
    profile = Photographer(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile", response_model=PhotographerResponse)
def get_profile(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Photographer:
    return get_owned_profile(db, current_user)


@router.put("/profile", response_model=PhotographerResponse)
def update_profile(
    payload: PhotographerUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(require_photographer),
) -> Photographer:
    profile = get_owned_profile(db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
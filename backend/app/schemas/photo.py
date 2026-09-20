from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.photo import PhotoStatus


class PhotoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    image_url: str = Field(min_length=1, max_length=500)
    category: str | None = Field(default=None, max_length=100)
    status: PhotoStatus = PhotoStatus.DRAFT


class PhotoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    category: str | None = Field(default=None, max_length=100)
    status: PhotoStatus | None = None


class PhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    photographer_id: int
    title: str
    description: str | None
    image_url: str
    category: str | None
    status: PhotoStatus
    created_at: datetime
    updated_at: datetime
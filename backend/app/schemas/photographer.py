from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PhotographerCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=150)
    bio: str | None = Field(default=None, max_length=5000)


class PhotographerUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=150)
    bio: str | None = Field(default=None, max_length=5000)


class PhotographerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    display_name: str
    bio: str | None
    created_at: datetime
    updated_at: datetime
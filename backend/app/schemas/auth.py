from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class RegistrationRole(str, Enum):
    CUSTOMER = UserRole.CUSTOMER.value
    PHOTOGRAPHER = UserRole.PHOTOGRAPHER.value


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: RegistrationRole = RegistrationRole.CUSTOMER


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
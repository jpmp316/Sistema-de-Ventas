from datetime import datetime
import re
from typing import Annotated

from pydantic import AfterValidator, AliasPath, BaseModel, ConfigDict, Field


PASSWORD_REQUIREMENTS = "La contraseña debe tener minimo 8 caracteres e incluir mayúscula, minúscula, número y símbolo."


def validate_password(value: str) -> str:
    if not all(re.search(pattern, value) for pattern in (
        r"[A-Z]", r"[a-z]", r"[0-9]", r"[^A-Za-z0-9\s]",
    )):
        raise ValueError(PASSWORD_REQUIREMENTS)
    return value


SecurePassword = Annotated[
    str,
    Field(min_length=8, max_length=128, description=PASSWORD_REQUIREMENTS),
    AfterValidator(validate_password),
]


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: SecurePassword


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    password: SecurePassword | None = None


class PasswordChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(min_length=1, max_length=1024)
    new_password: SecurePassword


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str = Field(validation_alias=AliasPath("role", "name"))
    created_at: datetime
    updated_at: datetime | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    username: str
    role: str


class PaginatedUsers(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int
    total_pages: int

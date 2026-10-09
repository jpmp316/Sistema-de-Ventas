from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    updated_at: datetime | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class PaginatedUsers(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int
    total_pages: int

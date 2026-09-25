from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=255)
    price_cents: int = Field(..., ge=0, description="Precio del producto en centavos")
    stock: int = Field(..., ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=255)
    price_cents: int | None = Field(None, ge=0, description="Precio del producto en centavos")
    stock: int | None = Field(None, ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    price_cents: int
    stock: int
    created_at: datetime
    updated_at: datetime | None = None


class PaginatedProducts(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    total_pages: int

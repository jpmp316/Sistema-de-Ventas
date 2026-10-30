from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.category_schemas import CategoryOut


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    category_id: int = Field(..., gt=0)
    description: str | None = Field(None, max_length=255)
    price_cents: int = Field(..., gt=0, description="Precio del producto en centavos")
    stock: int = Field(..., ge=0)
    min_stock: int = Field(..., ge=0)

    @field_validator("name", "code")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Este campo no puede estar vacío")
        return normalized


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=100)
    code: str | None = Field(None, min_length=1, max_length=50)
    category_id: int | None = Field(None, gt=0)
    description: str | None = Field(None, max_length=255)
    price_cents: int | None = Field(None, gt=0, description="Precio del producto en centavos")
    stock: int | None = Field(None, ge=0)
    min_stock: int | None = Field(None, ge=0)
    is_active: bool | None = None

    @field_validator("name", "code")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Este campo no puede estar vacío")
        return normalized


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    category_id: int
    category: CategoryOut
    description: str | None = None
    price_cents: int
    stock: int
    min_stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class PaginatedProducts(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    total_pages: int

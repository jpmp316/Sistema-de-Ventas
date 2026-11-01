from datetime import datetime
from decimal import Decimal

from pydantic import AliasPath, BaseModel, ConfigDict, Field, model_validator


class SaleLineCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SaleCreate(BaseModel):
    items: list[SaleLineCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_products(self):
        if len({item.product_id for item in self.items}) != len(self.items):
            raise ValueError("Cada producto debe aparecer una sola vez en la venta")
        return self


class SaleDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    product_name: str = Field(validation_alias=AliasPath("product", "name"))
    product_code: str = Field(validation_alias=AliasPath("product", "code"))
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    username: str = Field(validation_alias=AliasPath("user", "username"))
    date: datetime
    subtotal: Decimal
    total: Decimal
    status: str
    details: list[SaleDetailOut]


class PaginatedSales(BaseModel):
    items: list[SaleOut]
    total: int
    page: int
    page_size: int
    total_pages: int

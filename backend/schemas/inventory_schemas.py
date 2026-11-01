from datetime import datetime
from pydantic import BaseModel, ConfigDict


class InventoryMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    user_id: int
    sale_id: int | None
    type: str
    quantity: int
    previous_stock: int
    resulting_stock: int
    date: datetime
    product_name: str
    username: str


class PaginatedMovements(BaseModel):
    items: list[InventoryMovementOut]
    total: int
    page: int
    page_size: int
    total_pages: int

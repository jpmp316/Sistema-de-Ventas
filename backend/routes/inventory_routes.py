from datetime import date, datetime, time, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from auth.dependencies import get_current_user
from core.database import get_db
from models.sales import InventoryMovement
from models.user import User
from schemas.inventory_schemas import InventoryMovementOut, PaginatedMovements

router = APIRouter(prefix="/inventory", tags=["Inventario"])


@router.get("/movements", response_model=PaginatedMovements)
def list_movements(
    date_from: date | None = None,
    date_to: date | None = None,
    movement_type: str | None = Query(None, alias="type", max_length=20),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(InventoryMovement).order_by(InventoryMovement.date.desc(), InventoryMovement.id.desc())
    if date_from:
        query = query.filter(InventoryMovement.date >= datetime.combine(date_from, time.min, tzinfo=timezone.utc))
    if date_to:
        query = query.filter(InventoryMovement.date < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc))
    if movement_type:
        query = query.filter(InventoryMovement.type == movement_type)
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [InventoryMovementOut(
        id=row.id, product_id=row.product_id, user_id=row.user_id, sale_id=row.sale_id,
        type=row.type, quantity=row.quantity, previous_stock=row.previous_stock,
        resulting_stock=row.resulting_stock, date=row.date,
        product_name=row.product.name, username=row.user.username,
    ) for row in rows]
    return PaginatedMovements(items=items, total=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size)

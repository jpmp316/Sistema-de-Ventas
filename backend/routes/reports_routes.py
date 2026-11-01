from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from auth.dependencies import require_admin
from core.database import get_db
from models.category import Category
from models.product import Product
from models.sales import Sale, SaleDetail, InventoryMovement
from models.user import User

# Colombia usa UTC-5 durante todo el año; no requiere datos IANA en Windows.
REPORT_TIMEZONE = timezone(timedelta(hours=-5))


def local_day(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(REPORT_TIMEZONE).date().isoformat()


router = APIRouter(prefix="/reports", tags=["Reportes"])


@router.get("/summary")
def report_summary(days: int = Query(7, ge=1, le=365), _current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    since = (now.astimezone(REPORT_TIMEZONE) - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    previous_since = since - timedelta(days=days)
    sales = db.query(Sale).filter(Sale.date >= since, Sale.date <= now, Sale.status == "completed").order_by(Sale.date).all()
    previous_sales = db.query(Sale).filter(Sale.date >= previous_since, Sale.date < since, Sale.status == "completed").all()
    by_day = {(since.astimezone(REPORT_TIMEZONE).date() + timedelta(days=offset)).isoformat(): {"day": (since.astimezone(REPORT_TIMEZONE).date() + timedelta(days=offset)).isoformat(), "revenue": 0.0, "operations": 0} for offset in range(days)}
    for sale in sales:
        key = local_day(sale.date)
        slot = by_day.setdefault(key, {"day": key, "revenue": 0.0, "operations": 0})
        slot["revenue"] += float(sale.total)
        slot["operations"] += 1
    top = (db.query(Product.name, func.sum(SaleDetail.quantity).label("quantity"))
           .join(SaleDetail, SaleDetail.product_id == Product.id)
           .join(Sale, Sale.id == SaleDetail.sale_id)
           .filter(Sale.date >= since, Sale.date <= now, Sale.status == "completed")
           .group_by(Product.id, Product.name).order_by(func.sum(SaleDetail.quantity).desc()).limit(5).all())
    low_stock = db.query(Product).filter(Product.is_active.is_(True), Product.stock <= Product.min_stock).count()
    movements = db.query(InventoryMovement).filter(InventoryMovement.date >= since, InventoryMovement.date <= now).count()
    inventory_days = {(since.astimezone(REPORT_TIMEZONE).date() + timedelta(days=offset)).isoformat(): {"day": (since.astimezone(REPORT_TIMEZONE).date() + timedelta(days=offset)).isoformat(), "entries": 0, "sales": 0, "adjustments": 0} for offset in range(days)}
    for movement in db.query(InventoryMovement).filter(InventoryMovement.date >= since, InventoryMovement.date <= now).all():
        key = local_day(movement.date)
        slot = inventory_days.setdefault(key, {"day": key, "entries": 0, "sales": 0, "adjustments": 0})
        if movement.type == "sale": slot["sales"] += movement.quantity
        elif movement.type in ("entry", "purchase"): slot["entries"] += movement.quantity
        else: slot["adjustments"] += movement.quantity
    category_stock = (db.query(Product.category_id, func.sum(Product.stock).label("units"))
                      .filter(Product.is_active.is_(True)).group_by(Product.category_id).all())
    categories = {category.id: category.name for category in db.query(Category).all()}
    prev_revenue = sum((s.total for s in previous_sales), Decimal("0.00"))
    revenue = sum((s.total for s in sales), Decimal("0.00"))
    average_ticket = (revenue / len(sales)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if sales else Decimal("0.00")
    return {"days": days, "revenue": float(revenue), "operations": len(sales),
            "previous_revenue": float(prev_revenue), "previous_operations": len(previous_sales),
            "average_ticket": float(average_ticket),
            "low_stock_products": low_stock, "inventory_movements": movements,
            "sales_by_day": list(by_day.values()), "inventory_by_day": list(inventory_days.values()),
            "stock_by_category": [{"category": categories.get(category_id, "Sin categoría"), "units": int(units or 0)} for category_id, units in category_stock],
            "top_products": [{"name": name, "quantity": int(quantity or 0)} for name, quantity in top]}

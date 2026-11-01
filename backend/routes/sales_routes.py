from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from core.database import get_db
from models.product import Product
from models.sales import InventoryMovement, Sale, SaleDetail
from models.user import User
from schemas.sales_schemas import PaginatedSales, SaleCreate, SaleOut

router = APIRouter(prefix="/sales", tags=["Ventas"])


@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    products = {}
    subtotal = Decimal("0.00")
    for line in payload.items:
        product = db.query(Product).filter(Product.id == line.product_id).with_for_update().first()
        if not product or not product.is_active:
            raise HTTPException(status_code=404, detail=f"Producto {line.product_id} no existe o está inactivo")
        if product.stock < line.quantity:
            raise HTTPException(status_code=409, detail=f"Stock insuficiente para {product.name}")
        products[line.product_id] = product
        subtotal += Decimal(product.price_cents) / 100 * line.quantity

    sale = Sale(user_id=current_user.id, subtotal=subtotal, total=subtotal)
    for line in payload.items:
        product = products[line.product_id]
        previous = product.stock
        unit_price = Decimal(product.price_cents) / 100
        line_subtotal = unit_price * line.quantity
        product.stock -= line.quantity
        sale.details.append(SaleDetail(product_id=product.id, quantity=line.quantity, unit_price=unit_price, subtotal=line_subtotal))
        db.add(InventoryMovement(product_id=product.id, user_id=current_user.id, sale=sale, type="sale", quantity=line.quantity, previous_stock=previous, resulting_stock=product.stock))
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/", response_model=PaginatedSales)
def list_sales(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), _current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Sale).order_by(Sale.date.desc(), Sale.id.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedSales(items=items, total=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, _current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale

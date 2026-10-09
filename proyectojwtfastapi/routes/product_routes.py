from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from core.database import get_db
from models.product import Product
from models.user import User
from schemas.product_schemas import (
    PaginatedProducts,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)

router = APIRouter()


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    return product


@router.post("/products/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = product_in.name.strip()

    if db.query(Product).filter(Product.name == name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del producto ya existe",
        )

    product = Product(
        name=name,
        description=product_in.description,
        price_cents=product_in.price_cents,
        stock=product_in.stock,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get("/products/", response_model=PaginatedProducts)
def list_products(
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(Product).order_by(Product.id).all()

    return PaginatedProducts(
        items=items,
        total=len(items),
        page=1,
        page_size=len(items),
        total_pages=1 if items else 0,
    )


@router.get("/products/paginated", response_model=PaginatedProducts)
def paginated_products(
    page: int = 1,
    page_size: int = 10,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    query = db.query(Product).order_by(Product.id)

    total = query.count()

    items = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = (total + page_size - 1) // page_size if total else 0

    return PaginatedProducts(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_product_or_404(db, product_id)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = get_product_or_404(db, product_id)

    if product_in.name is not None:
        name = product_in.name.strip()

        if db.query(Product).filter(
            Product.name == name,
            Product.id != product_id,
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre del producto ya existe",
            )

        product.name = name

    if product_in.description is not None:
        product.description = product_in.description

    if product_in.price_cents is not None:
        product.price_cents = product_in.price_cents

    if product_in.stock is not None:
        product.stock = product_in.stock

    db.commit()
    db.refresh(product)

    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = get_product_or_404(db, product_id)

    db.delete(product)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

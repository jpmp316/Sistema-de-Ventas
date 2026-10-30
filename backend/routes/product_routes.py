from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from core.database import get_db
from models.category import Category
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
    code = product_in.code.strip()
    category = db.query(Category).filter(Category.id == product_in.category_id).first()
    if not category:
        raise HTTPException(status_code=422, detail="La categoría seleccionada no existe")

    if db.query(Product).filter(Product.name == name).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre del producto ya existe",
        )

    if db.query(Product).filter(func.lower(Product.code) == code.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El código del producto ya existe",
        )

    product = Product(
        name=name,
        code=code,
        category=category,
        description=product_in.description,
        price_cents=product_in.price_cents,
        stock=product_in.stock,
        min_stock=product_in.min_stock,
    )

    db.add(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese nombre o código",
        ) from exc
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
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre del producto ya existe",
            )

        product.name = name

    if "code" in product_in.model_fields_set:
        if product_in.code is None:
            raise HTTPException(status_code=422, detail="El código no puede ser nulo")
        code = product_in.code.strip()
        if db.query(Product).filter(
            func.lower(Product.code) == code.lower(),
            Product.id != product_id,
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El código del producto ya existe",
            )
        product.code = code

    if "category_id" in product_in.model_fields_set:
        if product_in.category_id is None:
            raise HTTPException(status_code=422, detail="La categoría no puede ser nula")
        category = db.query(Category).filter(Category.id == product_in.category_id).first()
        if not category:
            raise HTTPException(status_code=422, detail="La categoría seleccionada no existe")
        product.category = category

    if "description" in product_in.model_fields_set:
        product.description = product_in.description

    if product_in.price_cents is not None:
        product.price_cents = product_in.price_cents

    if product_in.stock is not None:
        product.stock = product_in.stock

    if product_in.min_stock is not None:
        product.min_stock = product_in.min_stock

    if product_in.is_active is not None:
        product.is_active = product_in.is_active

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese nombre o código",
        ) from exc
    db.refresh(product)

    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = get_product_or_404(db, product_id)

    product.is_active = False
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

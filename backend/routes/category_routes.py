from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from core.database import get_db
from models.category import Category
from models.product import Product
from models.user import User
from schemas.category_schemas import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter()


def get_category_or_404(db: Session, category_id: int) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.get("/categories/", response_model=list[CategoryOut])
def list_categories(
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Category).order_by(Category.name).all()


@router.post("/categories/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = category_in.name.strip()
    if db.query(Category).filter(func.lower(Category.name) == name.lower()).first():
        raise HTTPException(status_code=409, detail="La categoría ya existe")

    category = Category(name=name)
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="La categoría ya existe") from exc
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = get_category_or_404(db, category_id)
    name = category_in.name.strip()
    if db.query(Category).filter(
        func.lower(Category.name) == name.lower(),
        Category.id != category_id,
    ).first():
        raise HTTPException(status_code=409, detail="La categoría ya existe")

    category.name = name
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="La categoría ya existe") from exc
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = get_category_or_404(db, category_id)
    if db.query(Product.id).filter(Product.category_id == category_id).first():
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar una categoría que tiene productos asociados",
        )

    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

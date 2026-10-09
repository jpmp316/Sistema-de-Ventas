from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.auth_handler import crear_token
from auth.auth_service import hashear_password, verificar_password
from auth.dependencies import get_current_user
from core.database import get_db
from models.user import User
from schemas.user_schemas import (
    PaginatedUsers,
    Token,
    UserCreate,
    UserOut,
    UserUpdate,
)

router = APIRouter()


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return user


@router.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    username = form_data.username.strip().lower()

    user = db.query(User).filter(User.username == username).first()

    if not user or not verificar_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = crear_token({"sub": user.username})

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=30 * 60,
    )


@router.post("/users/",response_model=UserOut,status_code=status.HTTP_201_CREATED,)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    username = user_in.username.strip().lower()

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe",
        )

    user = User(
        username=username,
        hashed_password=hashear_password(user_in.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/users/", response_model=PaginatedUsers)
def list_users(
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.query(User).order_by(User.id).all()

    return PaginatedUsers(
        items=items,
        total=len(items),
        page=1,
        page_size=len(items),
        total_pages=1 if items else 0,
    )


@router.get("/users/paginated", response_model=PaginatedUsers)
def paginated_users(
    page: int = 1,
    page_size: int = 10,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)

    query = db.query(User).order_by(User.id)

    total = query.count()

    items = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = (total + page_size - 1) // page_size if total else 0

    return PaginatedUsers(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_or_404(db, user_id)


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_or_404(db, user_id)

    if user_in.username is not None:
        username = user_in.username.strip().lower()

        if db.query(User).filter(
            User.username == username,
            User.id != user_id,
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe",
            )

        user.username = username

    if user_in.password is not None:
        user.hashed_password = hashear_password(user_in.password)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = get_user_or_404(db, user_id)

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

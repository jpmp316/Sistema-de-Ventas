from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.auth_handler import ACCESS_TOKEN_EXPIRE_MINUTES, crear_token, verificar_token
from auth.auth_service import hashear_password, verificar_password
from auth.dependencies import get_current_user
from core.database import get_db
from models.user import User
from models.role import Role
from schemas.user_schemas import (
    PaginatedUsers,
    Token,
    UserCreate,
    UserOut,
    UserUpdate,
)

router = APIRouter()
optional_bearer = HTTPBearer(auto_error=False)


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    payload = verificar_token(credentials.credentials)
    username = payload.get("sub") if payload else None
    return db.query(User).filter(User.username == username).first() if username else None


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
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        username=user.username,
        role=user.role.name,
    )


@router.post("/users/",response_model=UserOut,status_code=status.HTTP_201_CREATED,)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    username = user_in.username.strip().lower()

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya existe",
        )

    if current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede crear usuarios")

    user = User(
        username=username,
        hashed_password=hashear_password(user_in.password),
        role=db.query(Role).filter(Role.name == "vendedor").one(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/auth/bootstrap-admin", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    has_users = db.query(User).count() != 0
    if has_users and (current_user is None or current_user.role.name != "admin"):
        raise HTTPException(status_code=403, detail="Se requiere una sesión de administrador para crear otro administrador")
    username = user_in.username.strip().lower()
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail="El nombre de usuario ya existe")
    admin_role = db.query(Role).filter(Role.name == "admin").one()
    user = User(username=username, hashed_password=hashear_password(user_in.password), role=admin_role)
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

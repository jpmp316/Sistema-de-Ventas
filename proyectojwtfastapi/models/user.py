from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="Id único del usuario")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="Nombre de usuario único")
    hashed_password = Column(String(255), nullable=False, comment="Contraseña hasheada del usuario")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Fecha y hora de creación del usuario")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Fecha y hora de la última actualización del usuario")

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise ValueError("El nombre de usuario no puede estar vacío")

        normalized = username.strip().lower()
        if len(normalized) < 3 or len(normalized) > 50:
            raise ValueError("El nombre de usuario debe tener entre 3 y 50 caracteres")

        if not normalized.replace("_", "").replace("-", "").isalnum():
            raise ValueError("El nombre de usuario solo puede contener letras, números y guiones bajos")
        return normalized
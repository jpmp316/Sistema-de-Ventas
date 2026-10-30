from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, func
from sqlalchemy.orm import validates

from core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("uq_categories_name_lower", func.lower(name), unique=True),
    )

    @validates("name")
    def validate_name(self, key, name):
        normalized = name.strip() if name else ""
        if not normalized or len(normalized) > 100:
            raise ValueError("El nombre de categoría es obligatorio y admite máximo 100 caracteres")
        return normalized

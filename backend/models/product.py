from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship, validates

from core.database import Base
from models.category import Category


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, comment="Id único del producto")
    name = Column(String(100), unique=True, index=True, nullable=False, comment="Nombre del producto")
    code = Column(String(50), nullable=False, comment="Código único del producto")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    description = Column(String(255), nullable=True, comment="Descripción del producto")
    price_cents = Column(Integer, nullable=False, comment="Precio del producto en centavos")
    stock = Column(Integer, nullable=False, comment="Cantidad de stock disponible del producto")
    min_stock = Column(Integer, nullable=False, default=0, server_default="0", comment="Stock mínimo del producto")
    is_active = Column(Boolean, nullable=False, default=True, server_default="true", comment="Indica si el producto está activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Fecha y hora de creación del producto")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Fecha y hora de la última actualización del producto")

    __table_args__ = (
        Index("uq_products_code_lower", func.lower(code), unique=True),
    )

    category = relationship(Category, backref="products")

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("El nombre del producto no puede estar vacío")

        normalized = name.strip()
        if len(normalized) < 3 or len(normalized) > 100:
            raise ValueError("El nombre del producto debe tener entre 3 y 100 caracteres")

        return normalized

    @validates("code")
    def validate_code(self, key, code):
        if not code or not code.strip():
            raise ValueError("El código del producto no puede estar vacío")
        return code.strip()

    @validates("price_cents")
    def validate_price_cents(self, key, price_cents):
        if price_cents <= 0:
            raise ValueError("El precio debe ser mayor que cero")

        return price_cents

    @validates("stock")
    def validate_stock(self, key, stock):
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")

        return stock

    @validates("min_stock")
    def validate_min_stock(self, key, min_stock):
        if min_stock < 0:
            raise ValueError("El stock mínimo no puede ser negativo")
        return min_stock

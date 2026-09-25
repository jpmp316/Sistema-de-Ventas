from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, comment="Id único del producto")
    name = Column(String(100), unique=True, index=True, nullable=False, comment="Nombre del producto")
    description = Column(String(255), nullable=True, comment="Descripción del producto")
    price_cents = Column(Integer, nullable=False, comment="Precio del producto en centavos")
    stock = Column(Integer, nullable=False, comment="Cantidad de stock disponible del producto")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Fecha y hora de creación del producto")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Fecha y hora de la última actualización del producto")

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("El nombre del producto no puede estar vacío")

        normalized = name.strip()
        if len(normalized) < 3 or len(normalized) > 100:
            raise ValueError("El nombre del producto debe tener entre 3 y 100 caracteres")

        return normalized

    @validates("price_cents")
    def validate_price_cents(self, key, price_cents):
        if price_cents < 0:
            raise ValueError("El precio no puede ser negativo")

        return price_cents

    @validates("stock")
    def validate_stock(self, key, stock):
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")

        return stock
"""Create the initial users and products schema.

Revision ID: 0001_initial_schema
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False, comment="Id único del producto"),
        sa.Column("name", sa.String(length=100), nullable=False, comment="Nombre del producto"),
        sa.Column("description", sa.String(length=255), nullable=True, comment="Descripción del producto"),
        sa.Column("price_cents", sa.Integer(), nullable=False, comment="Precio del producto en centavos"),
        sa.Column("stock", sa.Integer(), nullable=False, comment="Cantidad de stock disponible del producto"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False, comment="Fecha y hora de creación del producto"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False, comment="Fecha y hora de la última actualización del producto"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_id", "products", ["id"], unique=False)
    op.create_index("ix_products_name", "products", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, comment="Id único del usuario"),
        sa.Column("username", sa.String(length=50), nullable=False, comment="Nombre de usuario único"),
        sa.Column("hashed_password", sa.String(length=255), nullable=False, comment="Contraseña hasheada del usuario"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False, comment="Fecha y hora de creación del usuario"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False, comment="Fecha y hora de la última actualización del usuario"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")

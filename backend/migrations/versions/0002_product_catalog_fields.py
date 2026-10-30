"""Add product codes, categories, minimum stock, and active state.

Revision ID: 0002_product_catalog_fields
Revises: 0001_initial_schema
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_product_catalog_fields"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_id", "categories", ["id"], unique=False)
    op.create_index(
        "uq_categories_name_lower",
        "categories",
        [sa.text("lower(name)")],
        unique=True,
    )
    op.execute("INSERT INTO categories (name) VALUES ('Sin categoría')")

    op.add_column("products", sa.Column("code", sa.String(length=50), nullable=True))
    op.add_column("products", sa.Column("category_id", sa.Integer(), nullable=True))
    op.add_column(
        "products",
        sa.Column("min_stock", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.execute(
        "UPDATE products "
        "SET code = 'LEGACY-' || CAST(id AS VARCHAR) "
        "WHERE code IS NULL"
    )
    op.execute(
        "UPDATE products SET category_id = "
        "(SELECT id FROM categories WHERE name = 'Sin categoría') "
        "WHERE category_id IS NULL"
    )
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "code",
            existing_type=sa.String(length=50),
            nullable=False,
        )
        batch_op.alter_column(
            "category_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_products_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    op.create_index("uq_products_code_lower", "products", [sa.text("lower(code)")], unique=True)


def downgrade() -> None:
    op.drop_index("uq_products_code_lower", table_name="products")
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint("fk_products_category_id_categories", type_="foreignkey")
        batch_op.drop_column("is_active")
        batch_op.drop_column("min_stock")
        batch_op.drop_column("category_id")
        batch_op.drop_column("code")
    op.drop_index("uq_categories_name_lower", table_name="categories")
    op.drop_index("ix_categories_id", table_name="categories")
    op.drop_table("categories")

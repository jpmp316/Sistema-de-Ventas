"""Normalize roles and add sales and inventory movement tables."""
from alembic import op
import sqlalchemy as sa

revision = "0004_roles_sales_inventory"
down_revision = "0003_user_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255)),
    )
    op.execute("INSERT INTO roles (name, description) VALUES ('admin', 'Administrador del sistema'), ('vendedor', 'Usuario vendedor')")
    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.execute("UPDATE users SET role_id = (SELECT id FROM roles WHERE roles.name = users.role)")
    with op.batch_alter_table("users") as batch:
        batch.alter_column("role_id", existing_type=sa.Integer(), nullable=False)
        batch.create_foreign_key("fk_users_role_id_roles", "roles", ["role_id"], ["id"], ondelete="RESTRICT")
        batch.drop_column("role")

    op.add_column("categories", sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), server_default="completed", nullable=False),
    )
    op.create_table(
        "sale_details",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
    )
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="RESTRICT")),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("previous_stock", sa.Integer(), nullable=False),
        sa.Column("resulting_stock", sa.Integer(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("inventory_movements")
    op.drop_table("sale_details")
    op.drop_table("sales")
    op.drop_column("categories", "is_active")
    op.add_column("users", sa.Column("role", sa.String(20), server_default="vendedor", nullable=False))
    op.execute("UPDATE users SET role = (SELECT name FROM roles WHERE roles.id = users.role_id)")
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("fk_users_role_id_roles", type_="foreignkey")
        batch.drop_column("role_id")
    op.drop_table("roles")

"""Add user roles."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_user_roles"
down_revision: Union[str, None] = "0002_product_catalog_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), server_default="admin", nullable=False))
    op.alter_column("users", "role", server_default="vendedor")


def downgrade() -> None:
    op.drop_column("users", "role")

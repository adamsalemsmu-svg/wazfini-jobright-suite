"""Ensure users table has updated_at column

Revision ID: r20251028_users_updated_at
Revises: r20250227_locale_tz
Create Date: 2025-10-28 12:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "r20251028_users_updated_at"
down_revision: Union[str, None] = "r20250227_locale_tz"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at if it does not exist yet.
    op.add_column(
        "users",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "updated_at")

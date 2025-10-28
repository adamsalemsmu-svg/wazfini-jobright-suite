"""Ensure users table has updated_at column

Revision ID: r20251028_users_updated_at
Revises: r20250227_locale_tz
Create Date: 2025-10-28 12:00:00

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "r20251028_users_updated_at"
down_revision: Union[str, None] = "r20250227_locale_tz"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure the column exists and any nulls are normalized.
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE"
    )
    op.execute(
        "UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"
    )
    op.execute(
        "ALTER TABLE users ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP"
    )
    op.execute("ALTER TABLE users ALTER COLUMN updated_at SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS updated_at")

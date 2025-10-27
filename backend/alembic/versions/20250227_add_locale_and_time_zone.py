"""Add locale and time_zone columns to users

Revision ID: 20250227_add_locale_and_time_zone
Revises: 20240523_add_full_name
Create Date: 2025-10-27 03:30:00

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20250227_add_locale_and_time_zone"
down_revision: Union[str, None] = "20240523_add_full_name"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns if missing (safe for existing production DBs)
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS locale VARCHAR(10) DEFAULT 'en'"
    )
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS time_zone VARCHAR(50) DEFAULT 'UTC'"
    )


def downgrade() -> None:
    # Remove columns if present
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS time_zone")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS locale")

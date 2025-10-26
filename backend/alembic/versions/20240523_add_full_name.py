"""Add full_name to existing users table

Revision ID: 20240523_add_full_name
Revises: 5f80b5f3edd6
Create Date: 2025-10-26 08:05:00

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "20240523_add_full_name"
down_revision: Union[str, None] = "5f80b5f3edd6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Column was missing on existing production databases; add it if absent.
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)")


def downgrade() -> None:
    op.drop_column("users", "full_name")

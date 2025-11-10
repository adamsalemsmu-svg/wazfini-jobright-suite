"""add resume-related fields to users

Revision ID: 20251110_add_user_resume_fields
Revises: r20251028_users_updated_at
Create Date: 2025-11-10 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251110_add_user_resume_fields"
down_revision: str | None = "r20251028_users_updated_at"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column(
        "users", sa.Column("linkedin_url", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "users", sa.Column("github_url", sa.String(length=255), nullable=True)
    )
    op.add_column("users", sa.Column("resume_skills", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "resume_skills")
    op.drop_column("users", "github_url")
    op.drop_column("users", "linkedin_url")
    op.drop_column("users", "phone")

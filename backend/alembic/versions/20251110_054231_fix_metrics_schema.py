"""fix metrics schema - add indexes and nullable constraints

Revision ID: 20251110_054231_fix_metrics_schema
Revises: 20251110_add_user_resume_fields
Create Date: 2025-11-10T05:42:31.606175
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20251110_054231_fix_metrics_schema"
down_revision: str | None = "20251110_add_user_resume_fields"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Make status and created_at nullable to match model
    op.alter_column('metrics', 'status', nullable=True, existing_type=sa.String(length=50))
    op.alter_column('metrics', 'created_at', nullable=True, existing_type=sa.DateTime())
    
    # Add indexes that exist in the model
    op.create_index(op.f('ix_metrics_id'), 'metrics', ['id'], unique=False)
    op.create_index(op.f('ix_metrics_task_id'), 'metrics', ['task_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_metrics_task_id'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_id'), table_name='metrics')
    op.alter_column('metrics', 'created_at', nullable=False, existing_type=sa.DateTime())
    op.alter_column('metrics', 'status', nullable=False, existing_type=sa.String(length=50))

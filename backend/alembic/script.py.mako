"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | repr}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${up_revision | repr}
down_revision = ${down_revision | repr}
branch_labels = ${branch_labels | repr}
depends_on = ${depends_on | repr}


def upgrade() -> None:
    ${upgrade}


def downgrade() -> None:
    ${downgrade}

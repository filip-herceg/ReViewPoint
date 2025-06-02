"""add is_deleted column to users table

Revision ID: 20250602_add_is_deleted
Revises: 9fc3acc47815
Create Date: 2025-06-02
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20250602_add_is_deleted"
down_revision = "9fc3acc47815"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )


def downgrade():
    op.drop_column("users", "is_deleted")

"""Add file size field

Revision ID: 31eb30e5f037
Revises: 20250605_add_used_password_reset_tokens
Create Date: 2025-07-09 11:51:44.952649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31eb30e5f037'
down_revision: Union[str, None] = '20250605_add_used_password_reset_tokens'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

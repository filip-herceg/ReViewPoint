"""
Add used_password_reset_tokens table for one-time-use password reset tokens

Revision ID: 20250605_add_used_password_reset_tokens
Revises: 9fc3acc47815
Create Date: 2025-06-05 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a3b4c5d6e7f8"
down_revision = "f140e6f46727"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "used_password_reset_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nonce", sa.String(length=64), nullable=False),
        sa.Column("used_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_used_password_reset_tokens_email", "used_password_reset_tokens", ["email"]
    )
    op.create_index(
        "ix_used_password_reset_tokens_nonce", "used_password_reset_tokens", ["nonce"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_used_password_reset_tokens_email", table_name="used_password_reset_tokens"
    )
    op.drop_index(
        "ix_used_password_reset_tokens_nonce", table_name="used_password_reset_tokens"
    )
    op.drop_table("used_password_reset_tokens")

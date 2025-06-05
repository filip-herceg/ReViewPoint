"""
Add used_password_reset_tokens table for one-time-use password reset tokens
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "used_password_reset_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False, index=True),
        sa.Column("nonce", sa.String(length=64), nullable=False, index=True),
        sa.Column("used_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_used_password_reset_tokens_email", "used_password_reset_tokens", ["email"])
    op.create_index("ix_used_password_reset_tokens_nonce", "used_password_reset_tokens", ["nonce"])

def downgrade():
    op.drop_index("ix_used_password_reset_tokens_email", table_name="used_password_reset_tokens")
    op.drop_index("ix_used_password_reset_tokens_nonce", table_name="used_password_reset_tokens")
    op.drop_table("used_password_reset_tokens")

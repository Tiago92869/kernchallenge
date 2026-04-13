"""add revoked tokens table

Revision ID: c3d9f1a7b2e4
Revises: 90344f92a40f
Create Date: 2026-04-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d9f1a7b2e4"
down_revision = "90344f92a40f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "revoked_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=255), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("revoked_tokens", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_revoked_tokens_jti"), ["jti"], unique=True)


def downgrade():
    with op.batch_alter_table("revoked_tokens", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_revoked_tokens_jti"))

    op.drop_table("revoked_tokens")

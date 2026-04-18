"""add archived notification type

Revision ID: f7a1c2d9e4b6
Revises: c3d9f1a7b2e4
Create Date: 2026-04-18 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "f7a1c2d9e4b6"
down_revision = "c3d9f1a7b2e4"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE notification_type ADD VALUE IF NOT EXISTS 'ARCHIVED'")


def downgrade():
    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        # Map ARCHIVED to an existing value so type cast succeeds.
        op.execute(
            "UPDATE notifications SET notification_type = 'REMOVED' WHERE notification_type = 'ARCHIVED'"
        )
        op.execute("ALTER TYPE notification_type RENAME TO notification_type_old")
        op.execute("CREATE TYPE notification_type AS ENUM ('ADDED', 'REMOVED')")
        op.execute(
            "ALTER TABLE notifications ALTER COLUMN notification_type TYPE notification_type USING notification_type::text::notification_type"
        )
        op.execute("DROP TYPE notification_type_old")

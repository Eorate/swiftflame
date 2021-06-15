"""create blacklist_tokens table

Revision ID: cba24cda48db
Revises: 65b436e937eb
Create Date: 2021-06-15 12:01:41.441609

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cba24cda48db"
down_revision = "65b436e937eb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "blacklist_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("token", sa.String(500), unique=True, nullable=False),
        sa.Column("blacklisted_on", sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table("blacklist_tokens")

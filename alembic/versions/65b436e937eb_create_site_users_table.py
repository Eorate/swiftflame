"""create site_users table

Revision ID: 65b436e937eb
Revises: 290d703beec1
Create Date: 2021-06-02 11:36:45.826156

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "65b436e937eb"
down_revision = "290d703beec1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("registered_on", sa.DateTime, nullable=False),
        sa.Column("admin", sa.Boolean, nullable=False, default=False),
    )


def downgrade():
    op.drop_table("site_users")

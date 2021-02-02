"""create pets table

Revision ID: 290d703beec1
Revises:
Create Date: 2021-02-02 12:17:59.983944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "290d703beec1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("species", sa.String(10), nullable=False),
        sa.Column("breed", sa.String(20), nullable=False),
        sa.Column("sex", sa.String(1), nullable=False),
        sa.Column("colour_and_identifying_marks", sa.String(200), nullable=False),
        sa.Column("photo", sa.Text, nullable=True, default="default.png"),
    )


def downgrade():
    op.drop_table("pets")

"""ajout de la photo de justificatif sur les dépenses

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("depenses", sa.Column("photo", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("depenses", "photo")

"""ajout de la date d'acceptation des CGU (traçabilité RGPD)

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-18

"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "utilisateurs",
        sa.Column("cgu_acceptees_le", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("utilisateurs", "cgu_acceptees_le")

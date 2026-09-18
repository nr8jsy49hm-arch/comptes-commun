"""ajout des étiquettes libres (tags transversaux aux catégories)

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "etiquettes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )

    op.create_table(
        "depense_etiquettes",
        sa.Column("depense_id", sa.Integer(), sa.ForeignKey("depenses.id"), primary_key=True),
        sa.Column("etiquette_id", sa.Integer(), sa.ForeignKey("etiquettes.id"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("depense_etiquettes")
    op.drop_table("etiquettes")

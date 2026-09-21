"""ajout des budgets par catégorie (enveloppes)

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "budgets_categories",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("mois", sa.Date(), nullable=False),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("categorie_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
    )


def downgrade() -> None:
    op.drop_table("budgets_categories")

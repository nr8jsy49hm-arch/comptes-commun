"""ajout des dépenses récurrentes (loyer, abonnements) et du lien sur depenses

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "depenses_recurrentes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("montant", sa.Float(), nullable=False),
        sa.Column("jour_du_mois", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("partagee", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("categorie_id", sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column("payeur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id")),
        sa.Column("foyer_id", sa.Integer(), sa.ForeignKey("foyers.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column(
        "depenses",
        sa.Column("recurrente_id", sa.Integer(), sa.ForeignKey("depenses_recurrentes.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("depenses", "recurrente_id")
    op.drop_table("depenses_recurrentes")
